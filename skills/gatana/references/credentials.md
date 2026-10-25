# Credentials in Gatana

Use this file to set up credentials, to explain where a credential comes from, or to fix a credential error.

Docs: [Credentials](https://docs.gatana.ai/credentials/), [Profiles: credentials resolution](https://docs.gatana.ai/profiles/#credentials-resolution), [Secret stores](https://docs.gatana.ai/secret-stores/).

## Contents

- [Two parts: configuration and credential](#two-parts-configuration-and-credential)
- [Scopes](#scopes)
- [How Gatana finds the credential for a call](#how-gatana-finds-the-credential-for-a-call)
- [What reaches the server, per transport](#what-reaches-the-server-per-transport)
- [Give a credential](#give-a-credential)
- [OAuth setup](#oauth-setup)
- [The need-credentials result](#the-need-credentials-result)
- [Copy, read and delete credentials](#copy-read-and-delete-credentials)
- [Secret stores](#secret-stores)
- [Dashboard steps](#dashboard-steps)

## Two parts: configuration and credential

Gatana keeps two separate things for each server:

1. **The authorization configuration**, in `server.authorization`. It says what kind of secret the server needs and who owns it:

   ```typescript
   authorization: {
     method: 'apikey',                 // 'none' | 'apikey' | 'oauth' | 'oauth-client-credentials'
     apikeys: ['API_KEY'],             // names only, for 'apikey'
     credentialsScope: 'user',         // 'server' | 'user'
     toolRefreshCredentialPolicy: 'any', // 'server-scoped' | 'any' | 'skip'
   }
   ```

2. **The credentials**: the stored values. There can be one server credential, one per user, and one per profile. The client and the model never see them. Gatana puts them into the request when it calls the server.

Use a credential in the server configuration with an expression:

- An API key: `{{ credentials.keys.API_KEY }}` in `url`, `headers`, `env` or `command`.
- An OAuth token: write nothing. Gatana sends `Authorization: Bearer <token>`. Do not set an `Authorization` header yourself for an OAuth server.

## Scopes

| Scope     | Who uses it                                     | Typical use                                                       |
| --------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| `server`  | Everybody who can call the server               | A service account, a team API key, a read-only database user.     |
| `user`    | One person. Each person has their own.          | Mail, calendar, GitHub: each person acts as themselves.           |
| `profile` | Everybody whose session has that profile active | One credential for a team, a project, an agent or one MCP client. |

`credentialsScope` on the server is `server` or `user`. It is the base scope. A profile credential is an override on top of it, and it is optional.

To give a different credential to each MCP client (for example one for Claude Code and one for a CI agent), use a profile for each client. Attach the profile to the client's personal access token or connected OAuth client.

## How Gatana finds the credential for a call

1. If the method is `none`, Gatana uses no credential.
2. **Profile override.** Gatana checks the active profiles in priority order. It uses the first profile credential for this server that is valid. Valid means: same type as `authorization.method`, and for API keys, the same number of keys as `authorization.apikeys`. An invalid profile credential is skipped, without an error.
3. **Base scope.** If no profile credential applies:
   - `credentialsScope: 'server'`: the server credential. If there is none, the call fails.
   - `credentialsScope: 'user'`: the calling user's credential. If there is none, the call fails with `need-credentials`.

There is **no fallback** between the base scopes. A user-scoped server never uses a server credential, and a server-scoped server never uses a user credential.

Profile priority, highest first:

1. Profiles assigned to the user in locked mode.
2. Profiles assigned to one of the user's teams in locked mode.
3. Profiles assigned to the user.
4. Profiles assigned to one of the user's teams.
5. All other active profiles: URL parameter `?p=`, header `x-gatana-profile-id`, claim mapping, personal access token, connected client.

Inside one level, Gatana sorts by profile name. Only organization owners can lock an assignment.

Tool refresh is different. To read the tool list, Gatana uses `toolRefreshCredentialPolicy`:

- `server-scoped`: the server credential. Refresh fails if there is none. This is the default when you give `authorization` without the field.
- `any`: any stored credential of the right type: server, user or profile.
- `skip`: no credential.

## What reaches the server, per transport

| Transport                         | API key                                                                                     | OAuth token                                        | Per-user credential possible       |
| --------------------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------------------------------- |
| `httpstreaming`, `sse`            | Expressions in `url` and `headers`, filled for each call                                    | `Authorization` header for each call               | Yes                                |
| `openapi`                         | Expressions in `headers`, filled for each call                                              | `Authorization` header, if none is set             | Yes                                |
| `hosted`                          | The function's `credentials.apikeys`, for each call. `env` gets the server credential only. | `credentials.headers.authorization`, for each call | Yes, through the function argument |
| `stdio` with an HTTP `transport`  | `env` and `command` get the server credential only, at start                                | `Authorization` header for each call               | OAuth only                         |
| `stdio` with `transport: 'stdio'` | `env` and `command` get the server credential only, at start                                | Not supported                                      | No                                 |

Gatana restarts a `stdio` or `hosted` server when you set or change its credentials.

## Give a credential

Prefer the authorize link. The user types the secret into Gatana, and the secret never passes through the chat.

```typescript
const { url } = await codemode.gatanaApi.getMcpServerCredentialsAuthorizeUrl({
  serverSlug: 'acme',
  scope: 'server', // 'server' | 'user' | 'profile'
  // profileId: 'prfl_...',   // for scope 'profile'
  returnTo: 'thank-you-page',
});
```

- For `apikey`, the page asks for the key values. For `oauth`, it starts the provider's login.
- The link does not need a Gatana sign-in. It works one time, for 24 hours.
- A server or profile link needs permission to manage that credential: admin of the server, or maintainer of the profile.
- CLI: `gatana create creds <slug> --scope user|server` prints the link for OAuth.

If the user gives you the value, set it directly. The `type` must match `authorization.method`:

```typescript
// Server scope
await codemode.gatanaApi.updateMcpServerCredentialsServer({
  serverSlug: 'acme',
  body: { type: 'apikey', apikeys: [['ACME_API_KEY', '<value>']] },
});
// The current user's own credential
await codemode.gatanaApi.updateMcpServerCredentialsUser({ serverSlug: 'acme', body: { ... } });
// A profile's credential
await codemode.gatanaApi.updateMcpServerCredentialsProfile({ serverSlug: 'acme', profileId: 'prfl_...', body: { ... } });
```

- `apikeys` here is an array of `[name, value]` pairs. The names must match `authorization.apikeys`.
- OAuth: `{ type: 'oauth', tokenSet: { accessToken, refreshToken?, accessTokenExpiresAt?, idToken? } }`. `accessTokenExpiresAt` is a Unix time in milliseconds. Use this only to import tokens. Normally the user signs in through the link.
- Client credentials: `{ type: 'oauth-client-credentials', clientConfig: { clientId, clientSecret, clientAuthMethod, scopes? } }`.
- CLI: `gatana create creds <slug> -f keys.json --scope server|user`, with `[["ACME_API_KEY","<value>"]]` in the file. The CLI has no profile scope.

Do not write a key value again in your answers. Do not print the values that a read operation returns.

## OAuth setup

An `oauth` server needs two things before anybody can sign in:

1. **OAuth metadata** (`oauthMetadata`): the provider's authorize, token and registration endpoints. Get them with `discoverMcpServerOauth({ serverSlug })` for a remote server, or `discoverMcpServerOauth({ serverSlug, url: '<issuer or MCP URL>' })`. Then save the result with `patchServerV2({ slug, body: { oauthMetadata } })`.
2. **An OAuth client** (`oauthClientConfiguration`): `{ grantType: 'authorization_code', clientId, clientSecret?, clientAuthMethod, scopes? }`.
   - If the provider supports dynamic client registration, the dashboard registers a client with one click: server page > **Settings** > authorization > **Auto** next to the client ID. There is no public API for this step.
   - Otherwise the user registers an app with the provider. Use the **Redirect URI** that the server's **Settings** tab shows. Then save the client ID and secret with `patchServerV2`.
   - A client ID or secret can be a secret reference, for example `{{ secrets.vault.google_client_secret }}`.

Notes:

- For well-known services, **Add Server > Popular servers** in the dashboard does both steps.
- Use the `authorization_code` grant. The `device_code` grant exists, but some providers (for example Google) give fewer permissions with it.
- Some providers (for example Atlassian) return ID tokens with a different issuer than the metadata. Gatana refuses these tokens by default. An organization owner can turn on **Settings > Allow different OAuth issuer paths**.
- `oauth-client-credentials` needs only the metadata on the server. Each credential holds its own client ID and secret.

## The need-credentials result

When a call needs a credential that does not exist, the tool result looks like this:

```json
{
  "errorCode": "need-credentials",
  "authorizeUrl": "https://gatana.ai/api/v1/mcp-servers/oauth/gt_.../begin",
  "message": "This tool requires secondary authorization. ..."
}
```

What to do:

1. Give the `authorizeUrl` to the user as a link. Say what it is for: "Sign in to Linear for Gatana."
2. Wait until the user says that it is done. Then call the tool again.

Gatana sends the same result when the provider rejects a stored login, for example a revoked or expired refresh token. The message then says that the login was rejected. For a shared login (server or profile scope), everybody who uses it acts as the account that signs in. Tell the user this before they sign in.

If the missing credential is a server credential and the user cannot manage it, Gatana gives no link. The message says to contact the Gatana administrator. When Gatana knows who authorized a rejected shared login, the message names that person.

## Copy, read and delete credentials

- Copy to another scope: `copyMcpServerCredentials({ serverSlug, id, to: 'profile', profileId })`. Also `to: 'server'`, or `to: 'user'` with an optional `userId`. Use it to turn one person's login into a team credential on a profile.
- List without secrets: `listCredentialsV2({ serverId? })`, `getMcpServerCredentialsServer({ serverSlug })`, `getMcpServerCredentialsUser({ serverSlug })`, `getMcpServerCredentialsProfile({ serverSlug, profileId })`.
- Reveal secrets: `getCredentialSecretV2({ id })` and the `...Apikeys` operations. Do not call these unless the user asks, and do not print the values.
- Delete: `deleteCredentialV2({ id })`, or `deleteMcpServerCredentialsServer`, `...User`, `...Profile`.
- Each credential has its own audit trail: `listCredentialAuditLogsV2({ credentialId })`.

## Secret stores

An organization can connect external secret stores (for example AWS Secrets Manager). A server configuration can then hold a reference instead of a value: `{{ secrets.<store>.<name> }}`. Gatana reads the value at call time. Use this for values that every user shares and that are managed somewhere else. Credentials stay the right place for per-user and per-profile secrets.

## Dashboard steps

- **Server credential and own credential:** server page > **Credentials**. Admins of the server can set the shared credential there. Each user can set their own.
- **Method and scope:** server page > **Settings**, authorization section.
- **Profile credential:** **Profiles** > the profile > **Edit** on the server row.
