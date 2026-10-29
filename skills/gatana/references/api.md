# Gatana operations: MCP, Code Mode, REST and CLI

Docs: [Public API](https://docs.gatana.ai/public-api-introduction/), [Code Mode](https://docs.gatana.ai/code-mode/), [CLI](https://github.com/gatana-ai/gatana/tree/main/packages/gatana-cli).

Each operation has one name. Use it on the surface that you have:

| Surface   | How to call `createServerV2`                                                                            |
| --------- | ------------------------------------------------------------------------------------------------------- |
| MCP tool  | `gatana-api_createServerV2` with `{ "body": { ... } }`                                                  |
| Code Mode | `await codemode.gatanaApi.createServerV2({ body: { ... } })`                                            |
| REST      | `POST https://<org>.gatana.ai/api/v2/servers` with the body as JSON and `Authorization: Bearer <token>` |

The `gatana-api` tools take their arguments by parameter name: path and query parameters by their own names (`serverSlug`, `slug`, `profileId`), and the request body as `body`. In Code Mode, call `codemode_search_tools` first. It shows the exact arguments and the return shape of each tool.

The REST API also accepts an OAuth access token from Gatana. On-premise installs use their own host instead of `<org>.gatana.ai`. The full specifications: `https://api.gatana.ai/api/v1/openapi.json` and `https://api.gatana.ai/api/v2/openapi.json`.

## Servers

| Operation                                                          | REST                                                      | Purpose                                                       |
| ------------------------------------------------------------------ | --------------------------------------------------------- | ------------------------------------------------------------- |
| `listServersV2`                                                    | `GET /api/v2/servers`                                     | All servers you can read. Returns `{ servers }`.              |
| `getServerV2`                                                      | `GET /api/v2/servers/{slug}`                              | One server. You can send the result back to `updateServerV2`. |
| `createServerV2`                                                   | `POST /api/v2/servers`                                    | Create a server with its full configuration.                  |
| `patchServerV2`                                                    | `PATCH /api/v2/servers/{slug}`                            | Change some fields (JSON Merge Patch).                        |
| `updateServerV2`                                                   | `PUT /api/v2/servers/{slug}`                              | Replace the server configuration.                             |
| `deleteServerV2`                                                   | `DELETE /api/v2/servers/{slug}`                           | Delete a server.                                              |
| `getMcpServerRunningStatus`                                        | `GET /api/v1/mcp-servers/{serverSlug}/running-status`     | Status of a `stdio` or `hosted` server.                       |
| `startMcpServer`, `stopMcpServer`                                  | `POST /api/v1/mcp-servers/{serverSlug}/start` and `/stop` | Start or stop a `stdio` or `hosted` server.                   |
| `discoverMcpServerOauth`                                           | `GET /api/v1/mcp-servers/{serverSlug}/oauth/discover`     | Find the OAuth metadata.                                      |
| `testMcpServerOpenapi`                                             | `POST /api/v1/mcp-servers/{serverSlug}/openapi/test`      | Check an OpenAPI specification URL.                           |
| `listMcpServerFiles`, `createMcpServerFile`, `deleteMcpServerFile` | `/api/v1/mcp-servers/{serverSlug}/files`                  | Files for `stdio` and `hosted` servers.                       |
| `updateMcpServerSourceCode`                                        | `PUT /api/v1/mcp-servers/{serverSlug}/source-code`        | Upload a zip for a `hosted` server.                           |

## Tools

| Operation                          | REST                                                              | Purpose                                                                             |
| ---------------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `listMcpServerTools`               | `GET /api/v1/mcp-servers/{serverSlug}/tools`                      | Cached tools of one server, also disabled ones.                                     |
| `getToolsSearch`                   | `GET /api/v1/tools/search`                                        | Search the tools of all servers you can read.                                       |
| `updateMcpServerToolIsEnabled`     | `PUT /api/v1/mcp-servers/{serverSlug}/tools/{toolName}/isEnabled` | Body `{ value: boolean }`.                                                          |
| `updateMcpServerAllToolsIsEnabled` | `PUT /api/v1/mcp-servers/{serverSlug}/all-tools-isEnabled`        | Body `{ value: boolean }`.                                                          |
| `patchMcpServerTool`               | `PATCH /api/v1/mcp-servers/{serverSlug}/tools/{toolName}`         | Override name, description or input schema.                                         |
| `callMcpServerTool`                | `POST /api/v1/mcp-servers/{serverSlug}/tools/{toolName}/call`     | Call a tool over REST.                                                              |
| (REST only)                        | `POST /api/v1/tools/refresh?serverSlug=<slug>`                    | Refresh the tool cache. Needs `Accept: text/event-stream`. Not available as a tool. |

## Access

| Operation                                   | REST                                                                      | Purpose                                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `listMcpServerMembers`                      | `GET /api/v1/mcp-servers/{serverSlug}/members/`                           | Users and teams with a role.                                                              |
| `updateMcpServerMember`                     | `PUT /api/v1/mcp-servers/{serverSlug}/members/{memberType}/{memberId}`    | `memberType` is `users` or `teams`. Body `{ role: 'member' \| 'maintainer' \| 'admin' }`. |
| `deleteMcpServerMember`                     | `DELETE /api/v1/mcp-servers/{serverSlug}/members/{memberType}/{memberId}` | Remove a member.                                                                          |
| `getMcpServersAccessPreview`                | `GET /api/v1/mcp-servers/access-preview?userId=` or `?teamId=`            | What a user or team can reach, and why.                                                   |
| `listUsers`, `listTeams`, `listTeamMembers` | `/api/v1/users`, `/api/v1/teams`                                          | Find user and team IDs.                                                                   |

## Credentials

| Operation                                                   | REST                                                                                         | Purpose                                                                    |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| `getMcpServerCredentialsAuthorizeUrl`                       | `GET /api/v1/mcp-servers/{serverSlug}/credentials/authorize-url?scope=&profileId=&returnTo=` | A link where the user enters a key or signs in. Returns `{ method, url }`. |
| `updateMcpServerCredentialsServer`                          | `PUT /api/v1/mcp-servers/{serverSlug}/credentials/server`                                    | Set the shared credential.                                                 |
| `updateMcpServerCredentialsUser`                            | `PUT /api/v1/mcp-servers/{serverSlug}/credentials/user`                                      | Set your own credential.                                                   |
| `updateMcpServerCredentialsProfile`                         | `PUT /api/v1/mcp-servers/{serverSlug}/credentials/profiles/{profileId}`                      | Set a profile credential.                                                  |
| `getMcpServerCredentialsServer`, `...User`, `...Profile`    | `GET .../credentials/server`, `/user`, `/profile?profileId=`                                 | Metadata, no secrets.                                                      |
| `copyMcpServerCredentials`                                  | `POST /api/v1/mcp-servers/{serverSlug}/credentials/copy?id=&to=&profileId=&userId=`          | Copy to another scope.                                                     |
| `deleteMcpServerCredentialsServer`, `...User`, `...Profile` | `DELETE` on the same paths                                                                   | Delete one credential.                                                     |
| `listCredentialsV2`                                         | `GET /api/v2/credentials?serverId=`                                                          | All credentials you can read, no secrets.                                  |
| `getCredentialSecretV2`                                     | `GET /api/v2/credentials/{id}/secret`                                                        | Reveal values. Only when the user asks.                                    |
| `refreshCredentialV2`                                       | `POST /api/v2/credentials/{id}/refresh`                                                      | Refresh OAuth tokens now.                                                  |
| `listCredentialAuditLogsV2`                                 | `GET /api/v2/credentials/{credentialId}/audit-logs`                                          | Who used or changed a credential.                                          |

## Profiles

| Operation                                                    | REST                                                          | Purpose                                                                           |
| ------------------------------------------------------------ | ------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `listProfiles`                                               | `GET /api/v1/profiles?serverSlug=`                            | Profiles you can read.                                                            |
| `getProfile`                                                 | `GET /api/v1/profiles/{profileId}`                            | Returns `{ profile }` with `servers[].slug` and credential metadata.              |
| `createProfile`                                              | `POST /api/v1/profiles`                                       | Body `{ name, description, isOpenToAllUsers, isRestrictive, isCodeModeForced? }`. |
| `updateProfile`                                              | `PUT /api/v1/profiles/{profileId}`                            | Flags and `serverIds`. **`serverIds` replaces the list.** Send slugs.             |
| `deleteProfile`                                              | `DELETE /api/v1/profiles/{profileId}`                         | Delete.                                                                           |
| `listProfileTools`                                           | `GET /api/v1/profiles/{profileId}/tools`                      | Tool configuration per server.                                                    |
| `updateProfileServerTools`                                   | `PUT /api/v1/profiles/{profileId}/servers/{serverSlug}/tools` | Replace the tool configuration for one server.                                    |
| `createUserProfile`, `deleteUserProfile`, `patchUserProfile` | `/api/v1/users/{userId}/profiles`                             | Assign to a user. Body `{ profileId, isLockedByOrgOwner? }`.                      |
| `createTeamProfile`, `deleteTeamProfile`                     | `/api/v1/teams/{teamId}/profiles`                             | Assign to a team. Same body.                                                      |
| `createProfileClaimMapping`, `deleteProfileClaimMapping`     | `/api/v1/profiles/{profileId}/claim-mappings`                 | Body `{ claimKey, claimValue }`.                                                  |
| `listProfileDirectAssignments`                               | `GET /api/v1/profiles/{profileId}/direct-assignments`         | Users and teams with the profile.                                                 |
| `createProfileMaintainer`, `deleteProfileMaintainer`         | `/api/v1/profiles/{profileId}/maintainers`                    | Body `{ userId }`.                                                                |
| `patchConnectedClient`                                       | `PATCH /api/v1/connected-clients/{clientId}`                  | Body `{ profileIds }` attaches profiles to a connected client.                    |

Your own personal access tokens, and the profiles on them, can only be changed in the dashboard. A service account's tokens can be managed with a token too: `listServiceAccountPersonalAccessTokens`, `createServiceAccountPersonalAccessToken` (body `{ name, profileIds? }`) and `deleteServiceAccountPersonalAccessToken` on `/api/v1/service-accounts/{userId}/personal-access-tokens`, by an organization owner. The tokens that Gatana makes for its own tools, the `gatanaApi` tools among them, are refused there.

## The gatana CLI

Install: `npm install -g gatana`, `brew install gatana-ai/tap/gatana`, or `curl -fsSL https://github.com/gatana-ai/gatana/releases/latest/download/install.sh | sh`.

Sign in: `gatana config login <org>`. No organization yet: `gatana signup`, see [Create an organization](../SKILL.md#create-an-organization). Check: `gatana auth-info`. Add `-o json` to any command for machine-readable output.

Always give every flag. A command without a needed flag asks a question, and an agent cannot answer it.

| Command                                                                     | Purpose                                                                                                                      |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `gatana get servers` / `gatana get server <slug>`                           | List servers, or show one.                                                                                                   |
| `gatana describe server <slug>`                                             | The server, its last 5 events, its credentials and who has access to it.                                                     |
| `gatana create server remote <url> -s <slug>` (add `--sse` for SSE)         | Add a remote MCP server. Finds its OAuth and registers a client when the issuer permits it.                                  |
| `gatana create server openapi <spec-url> -s <slug>`                         | Add tools made from an OpenAPI specification.                                                                                |
| `gatana create server local -s <slug> <command...>`                         | Add a command such as `npx -y <package>`. Put the flags before the command.                                                  |
| `gatana create server code -s <slug> --runtime node24\|python313`           | Add hosted code. Then deploy it with `faas upload`.                                                                          |
| `gatana create server built-in <id>`                                        | Install a built-in server: `artifacts`, `skills`, `codemode`, `gatana-api`, `gatana-debug`, `fetch`, `compression`.          |
| `gatana create server email <provider> -s <slug> --access <a>`              | Add a mailbox: `gmail`, `microsoft365`, `fastmail`, `icloud`, `imap --imap-host <h>`, `jmap --session-url <u>`.              |
| `gatana patch server <slug> -f patch.json`                                  | Merge patch with the v2 server fields, for example `transportConfig` and `authorization`.                                    |
| `gatana delete server <slug>`                                               | Delete.                                                                                                                      |
| `gatana tools ls [--server <slug>] [--all]`                                 | The enabled tools. `--all` adds the disabled ones.                                                                           |
| `gatana tools <slug>_<tool>`                                                | Description and arguments of a tool, and an example call.                                                                    |
| `gatana tools call <slug>_<tool> -a key=value` or `-f args.json`            | Call a tool. `x` is short for `call`.                                                                                        |
| `gatana create creds <slug> --scope server\|user -f keys.json`              | Set API keys: `[["NAME","value"]]`. Without `-f` on an OAuth server: prints the authorize link.                              |
| `gatana get creds -s <slug>` / `gatana delete creds <id> -s <slug>`         | List or delete credentials.                                                                                                  |
| `gatana deploy get\|logs\|wait\|start\|stop <slug>`                         | Deployments of `stdio` and `hosted` servers.                                                                                 |
| `gatana faas init\|verify\|run\|upload\|download`                           | Hosted code. `faas upload <slug> <path> --create` creates and deploys.                                                       |
| `gatana server access <slug>`                                               | The accounts, teams and profiles with a role on a server, and the settings that give access to every member.                 |
| `gatana server grant\|revoke <slug> --account <email>`                      | Give a role on a server (`--role member\|maintainer\|admin`, default `member`), or take it away. `--team <name>` for a team. |
| `gatana get teams` / `gatana describe team <name>`                          | List teams, or show one with its members, invitations, server roles, profiles and claim mappings.                            |
| `gatana create team <name> -a <email>...` / `gatana delete team <name>`     | Create a team with members, or delete one.                                                                                   |
| `gatana team add-member\|remove-member <team> <email>...`                   | Add or remove members. `--role maintainer` lets a member manage the team.                                                    |
| `gatana team invitations add\|rm <team> <email>`                            | Invite a person by email, or delete the invitation.                                                                          |
| `gatana team claims add\|rm <team> <key>=<value>`                           | Make everyone whose identity provider sends the claim a member at sign-in.                                                   |
| `gatana get profiles` / `gatana describe profile <name>`                    | List profiles, or show one with its servers, members, maintainers and claim mappings.                                        |
| `gatana create profile <name> --description <text> -s <slug>...`            | Create a profile with servers. Add `--restrictive`, `--open-to-all` or `--code-mode` for those settings.                     |
| `gatana profile add-server\|remove-server <profile> <slug>...`              | Add or remove servers without replacing the list.                                                                            |
| `gatana profile assign\|unassign <profile> --account <email>`               | Give a profile to an account, or take it away. `--team <name>` for a team, `--lock` to lock (owners only).                   |
| `gatana profile claims add\|rm <profile> <key>=<value>`                     | Give the profile to everyone whose identity provider sends the claim.                                                        |
| `gatana profile tools <profile> <slug> [-f tools.json]`                     | Show the tool configuration of a profile for one server, or replace it.                                                      |
| `gatana patch profile <name> -p key=value` / `gatana delete profile <name>` | Change or delete a profile. `serverIds` in a patch replaces the list.                                                        |
| `gatana get accounts` / `gatana describe account <email>`                   | List accounts, or show one with its profiles and teams.                                                                      |
| `gatana create account <email> --name <name> --role member\|owner`          | Invite a user. Gatana sends the invitation email.                                                                            |
| `gatana create service-account <name>`                                      | Create a service account. Prints the API key of its first token.                                                             |
| `gatana create pat --account <email> --name <name> --profile <p>`           | Create a token for a service account and print its key. Your own tokens need the dashboard.                                  |
| `gatana patch account <email> -p isDisabled=true` / `delete account`        | Change or delete an account.                                                                                                 |
| `gatana get org` / `gatana patch org -p key=value`                          | Organization settings (owners only). A nested key merges with the stored value. `gatana schema org` lists the keys.          |

Profiles, accounts and teams go by name, email or ID. Quote a name that holds spaces.
