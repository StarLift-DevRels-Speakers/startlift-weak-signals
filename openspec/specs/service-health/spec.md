# service-health Specification

## Purpose

Exposes a liveness endpoint that reports whether the process is serving requests and which model it
is configured to use, so that orchestration and monitoring can probe the service without consuming
LLM quota.

## Requirements

### Requirement: Health endpoint

The service SHALL expose `GET /health` that reports the liveness of the process.

#### Scenario: Service is alive

- **WHEN** the endpoint is requested and the process is serving requests
- **THEN** the service responds with HTTP 200

#### Scenario: Health response identifies the configured model

- **WHEN** the endpoint is requested
- **THEN** the response identifies the model the service is configured to call for scoring

#### Scenario: Health check does not consume provider quota

- **WHEN** the endpoint is requested
- **THEN** the service does not call the LLM provider to answer it

#### Scenario: Health check requires no credentials

- **WHEN** the endpoint is requested by a caller that supplies no authentication
- **THEN** the service answers with its status rather than rejecting the request
