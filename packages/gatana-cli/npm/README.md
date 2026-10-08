# gatana

The command-line interface for [Gatana](https://gatana.ai): manage servers, tools, credentials and
skills.

```sh
npm install -g gatana
gatana config login https://<your-org>.gatana.ai
gatana get servers
```

The CLI is a native binary for macOS and Linux (arm64 and x64). npm installs the binary for your
machine from an optional dependency, `@gatana/cli-<os>-<cpu>`.

Other ways to install it:

```sh
brew install gatana-ai/tap/gatana
curl -fsSL https://github.com/gatana-ai/gatana/releases/latest/download/install.sh | sh
```

Documentation: [docs.gatana.ai](https://docs.gatana.ai) and the
[CLI README](https://github.com/gatana-ai/gatana/tree/main/packages/gatana-cli#readme), which lists
every command.
