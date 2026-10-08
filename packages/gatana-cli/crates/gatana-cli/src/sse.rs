//! A reader for `text/event-stream` responses: deployment progress and followed logs.

use anyhow::Result;
use futures_util::StreamExt;
use futures_util::stream::BoxStream;

#[derive(Debug, Clone, PartialEq)]
pub struct Event {
    /// `message` when the server named none.
    pub event: String,
    pub data: String,
}

pub struct EventStream {
    body: BoxStream<'static, reqwest::Result<Vec<u8>>>,
    buffer: Vec<u8>,
    parser: Parser,
}

impl EventStream {
    pub fn new(response: reqwest::Response) -> Self {
        let body = response.bytes_stream().map(|chunk| chunk.map(|bytes| bytes.to_vec())).boxed();
        Self { body, buffer: Vec::new(), parser: Parser::default() }
    }

    /// The next event, or None when the server closed the stream.
    pub async fn next(&mut self) -> Option<Result<Event>> {
        loop {
            while let Some(position) = self.buffer.iter().position(|byte| *byte == b'\n' || *byte == b'\r') {
                let line: Vec<u8> = self.buffer.drain(..position).collect();
                let terminator = self.buffer.remove(0);
                if terminator == b'\r' && self.buffer.first() == Some(&b'\n') {
                    self.buffer.remove(0);
                }
                if let Some(event) = self.parser.line(&String::from_utf8_lossy(&line)) {
                    return Some(Ok(event));
                }
            }
            match self.body.next().await {
                Some(Ok(chunk)) => self.buffer.extend_from_slice(&chunk),
                Some(Err(error)) => return Some(Err(error.into())),
                None => {
                    let rest = std::mem::take(&mut self.buffer);
                    if !rest.is_empty() {
                        self.parser.line(&String::from_utf8_lossy(&rest));
                    }
                    return self.parser.line("").map(Ok);
                }
            }
        }
    }
}

#[derive(Default)]
struct Parser {
    event: Option<String>,
    data: Vec<String>,
}

impl Parser {
    /// Feeds one line; a blank line dispatches the event collected so far.
    fn line(&mut self, line: &str) -> Option<Event> {
        if line.is_empty() {
            let event = self.event.take().unwrap_or_else(|| "message".to_string());
            if self.data.is_empty() {
                return None;
            }
            let data = std::mem::take(&mut self.data).join("\n");
            return Some(Event { event, data });
        }
        if line.starts_with(':') {
            return None;
        }
        let (field, value) = match line.split_once(':') {
            Some((field, value)) => (field, value.strip_prefix(' ').unwrap_or(value)),
            None => (line, ""),
        };
        match field {
            "event" => self.event = Some(value.to_string()),
            "data" => self.data.push(value.to_string()),
            _ => {}
        }
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn events_are_split_on_blank_lines_and_data_lines_join() {
        let mut parser = Parser::default();
        let mut events = Vec::new();
        for line in [": comment", "event: stdout", "data: {\"line\":\"a\"}", "", "data: one", "data: two", "", ""] {
            events.extend(parser.line(line));
        }
        assert_eq!(
            events,
            vec![
                Event { event: "stdout".into(), data: "{\"line\":\"a\"}".into() },
                Event { event: "message".into(), data: "one\ntwo".into() },
            ]
        );
    }
}
