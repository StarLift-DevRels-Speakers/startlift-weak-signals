# Spec Delta

## Purpose

Defines how the service is configured from the environment: the credentials used to call the LLM,
the model and generation limits used for scoring, and the address the HTTP server binds to.

## ADDED Requirements

### Requirement: Provider credentials are required and validated at startup

The GigaChat token SHALL be read from the environment under the name `GIGACHAT_TOKEN`, and the
service SHALL refuse to start when it is absent.

#### Scenario: Token is configured

- **WHEN** the process starts with `GIGACHAT_TOKEN` set
- **THEN** the token is available to the provider client and is never written to logs or error
  messages

#### Scenario: Token is missing

- **WHEN** the process starts without `GIGACHAT_TOKEN`
- **THEN** startup fails with an error that names the missing setting, and the server does not begin
  accepting requests

### Requirement: Provider settings have working defaults

All provider settings other than the token SHALL be overridable from the environment under the
`GIGACHAT_` prefix, and SHALL default to values that need no extra configuration for the intended
model: model `GigaChat-3-Ultra`, base URL `https://api.giga.chat/v1`, scope `GIGACHAT_API_PERS`,
temperature `0.1`, maximum response tokens `5000`, and TLS verification disabled.

#### Scenario: Only the token is provided

- **WHEN** the process starts with only `GIGACHAT_TOKEN` set
- **THEN** scoring uses the default model, base URL, scope, temperature, and token limit

#### Scenario: A setting is overridden

- **WHEN** a provider setting other than the token is present in the environment under the
  `GIGACHAT_` prefix
- **THEN** the overridden value is used instead of the default

#### Scenario: TLS verification default is explicit

- **WHEN** the provider client is created without an explicit override
- **THEN** certificate verification is disabled as a deliberate development setting, and it can be
  re-enabled through configuration without a code change

### Requirement: Server bind settings are configurable

The HTTP server host and port SHALL be configurable from the environment under the `SIGNALS_`
prefix and SHALL default to `0.0.0.0` and `8000`.

#### Scenario: Defaults are used

- **WHEN** no server setting is present in the environment
- **THEN** the process serves on `0.0.0.0:8000`

#### Scenario: Bind settings are overridden

- **WHEN** host or port is present in the environment under the `SIGNALS_` prefix
- **THEN** the process binds to those values

### Requirement: Startup lists the models available to the token

At startup the service SHALL request the list of models available to the configured credentials and
SHALL log it, so that a wrong or expired token and an unexpected model catalogue are visible without
sending a scoring request.

#### Scenario: Model list is retrieved

- **WHEN** the process starts with valid credentials
- **THEN** the available model identifiers are written to the process log before the server accepts
  requests

#### Scenario: Application logs reach the process output

- **WHEN** the process is started with the documented run command
- **THEN** the startup line naming the scoring model and the line listing the available models are
  visible in its output, so an operator sees them without a request being sent

#### Scenario: Configured model is not checked against the list

- **WHEN** the retrieved list does not contain the configured scoring model
- **THEN** the service still starts and scoring still uses the configured model

#### Scenario: Credentials are rejected during startup

- **WHEN** the model list request fails because the credentials are invalid or unreachable
- **THEN** startup fails and the server does not begin accepting requests
