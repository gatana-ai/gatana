use clap::Parser;
use gatana_cli::{cli::Cli, commands, output};
use std::process::ExitCode;

fn main() -> ExitCode {
    let cli = Cli::parse();
    output::set_format(cli.output);
    // One thread is plenty for a CLI, and it starts faster than a pool.
    let runtime = match tokio::runtime::Builder::new_current_thread().enable_all().build() {
        Ok(runtime) => runtime,
        Err(error) => {
            output::error(&format!("could not start: {error}"));
            return ExitCode::FAILURE;
        }
    };
    match runtime.block_on(commands::run(cli)) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) if error.downcast_ref::<commands::Silent>().is_some() => ExitCode::FAILURE,
        Err(error) => {
            output::error(&format!("{error:#}"));
            ExitCode::FAILURE
        }
    }
}
