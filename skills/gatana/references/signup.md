# Create a Gatana organization

Use this file when the user has no Gatana organization and wants to create one. The `gatana` CLI creates the organization and signs in to it. For installation instructions, read **The gatana CLI** in [api.md](api.md). Without the CLI, the user can open [Gatana sign-up](https://hello.gatana.ai/signup) in a browser.

## Values

Get these values from the user. Then confirm them in one sentence, because the command creates an organization and sends an email.

| Value             | Flag         | Rule                                                                                                                                                                                   |
| ----------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Organization name | `--org-name` | 1 to 50 characters.                                                                                                                                                                    |
| Organization ID   | `--org-id`   | Lowercase letters, digits and hyphens, 40 characters or fewer. The address is `https://<id>.gatana.ai`. Without the flag, the CLI makes it from the name: `Acme Inc` gives `acme-inc`. |
| Email address     | `--email`    | 50 characters or fewer. This person becomes the owner. Gatana sends a 6-digit code to the address.                                                                                     |

## Sign up

Sign up in two steps:

1. Run `gatana signup --org-name "Acme Inc" --email you@acme.com`. Gatana sends a 6-digit code to the address. The CLI prints the command to finish sign-up. It includes the organization ID and ends with `--code <code>`. The new organization gets a free 14-day Pro trial and moves to the free plan when the trial ends.
2. Ask the user for the code from the email. Run the printed command with `<code>` replaced by the code. The CLI creates the organization and signs in to it.

About the code:

- It is valid for 30 minutes. After 5 wrong tries, it stops working.
- If the CLI says that the code is wrong, ask the user to check it. Then run the printed command again.
- Run step 1 only one time. Each run without `--code` sends a new code, and the new code replaces the old one.

Two other ways:

- The user runs `gatana signup` in their own terminal. The CLI asks for each value and for the code.
- You run `gatana signup --browser --org-name "Acme Inc" --email you@acme.com` in the background. The CLI opens the sign-up page with the name and email filled in. It waits up to 10 minutes. Give the user the link that the CLI prints, in case the browser does not open. The user finishes the sign-up in the browser.

For an on-premise install, add `--base-url https://<address of the install>`.

## After the sign-up

- `gatana auth-info` shows the new organization.
- `gatana install` connects every AI agent it finds on the machine (Claude Code, Codex, Hermes, OpenClaw) to the gateway, without a question. To connect only some agents, name them: `gatana install claude` (or `codex`, `hermes`, `openclaw`).
- In the cloud, a new organization starts with a 14-day trial. Plans: [www.gatana.ai/pricing](https://www.gatana.ai/pricing).
- An owner who signed up in the terminal has no password for the dashboard yet. On the sign-in page, the owner clicks **Forgot your password?** and sets one from the email.

## Troubleshooting

| Symptom                                                     | Cause and fix                                                                                                           |
| ----------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `This organization ID is already taken` or `is not allowed` | `gatana signup` needs another organization ID. In a terminal, the CLI asks for one.                                     |
| `does not support sign-up in the terminal`                  | The Gatana version is older. Use `gatana signup --browser`.                                                             |
| `The code is wrong or has expired`                          | Ask the user to check the code. After 30 minutes or 5 wrong tries, run `gatana signup` without `--code` for a new code. |
