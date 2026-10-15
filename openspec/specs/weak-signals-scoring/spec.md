# weak-signals-scoring Specification

## Purpose

Scores a single conference speaker from weak signals: the service accepts a speaker profile with
numeric features and free-text context, asks the LLM for a bounded talent score, and returns that
score with its rationale and confidence.

## Requirements

### Requirement: Speaker scoring endpoint

The service SHALL expose `POST /signals/weak-signals` accepting a single speaker payload and
returning one talent score for that speaker.

#### Scenario: Valid speaker is scored

- **WHEN** a client posts a payload with valid speaker data
- **THEN** the service responds with HTTP 200 and a body containing the speaker id, a score, a
  reason, and a confidence

#### Scenario: Invalid payload is rejected

- **WHEN** a client posts a payload with a missing required field or a value outside its allowed
  range, such as a score span or a rating outside its bounds
- **THEN** the service responds with HTTP 422 and does not call the LLM

### Requirement: Scoring uses the fixed prompts and structured output

Scoring SHALL send the fixed system instruction and the fixed user message built from the speaker
payload, and SHALL request a response constrained to the score, reason, and confidence shape. The
resulting score SHALL be an integer from 1 to 5, the reason a non-empty string, and the confidence
one of `low`, `medium`, or `high`.

#### Scenario: Model response is constrained to the scoring shape

- **WHEN** the scoring service receives a model response
- **THEN** the response is interpreted as the score, reason, and confidence shape before any HTTP
  response is produced

#### Scenario: Prompt content is derived from the payload

- **WHEN** the user message is built from a speaker payload
- **THEN** it contains that speaker's profile, activity, quality, achievements, demand, recent talks,
  recent feedback, and external mentions, and it renders missing optional sections as an explicit
  absence marker instead of failing

### Requirement: Scoring response preserves the speaker identity

The returned score SHALL be associated with the id of the speaker from the request, and the response
SHALL contain only the speaker id, score, reason, and confidence.

#### Scenario: Identity is carried through

- **WHEN** a speaker with a given id is scored
- **THEN** the response id equals the request id and the response contains no model-internal fields

### Requirement: Provider failures map to distinct status codes

The service SHALL distinguish an unusable provider answer from a provider timeout and from an
unexpected internal failure, and SHALL report each with its own HTTP status code.

#### Scenario: Provider answer is unusable

- **WHEN** the provider fails, rejects the request, or returns content that cannot be parsed into the
  scoring shape
- **THEN** the service responds with HTTP 502 and logs the failure against the speaker id

#### Scenario: Provider times out

- **WHEN** the provider does not answer within the request timeout
- **THEN** the service responds with HTTP 504

#### Scenario: Unexpected failure

- **WHEN** scoring fails for any other reason
- **THEN** the service responds with HTTP 500 and logs the exception

#### Scenario: Failure detail is not leaked

- **WHEN** any provider or internal failure is reported
- **THEN** the response body contains no provider message, token, or stack trace
