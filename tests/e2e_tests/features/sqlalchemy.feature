Feature: As a User of Arrested
	I want to Create REST APIs using Arrested that integrate with SQLAlchemy
	So that I can expose data from a relational database to my users

  Background: Set target server address and headers
    Given I am using server "$SERVER_URL"
    And I set "Accept" header to "application/json"
    And I set "Content-Type" header to "application/json"

  Scenario: Test DBListMixin
    When I make a GET request to "/v1/characters"
    Then the response status should be 200
    And the response body should contain "payload"
    And the JSON array length at path "payload" should be 5

  Scenario: Test DBCreateMixin
    When I make a POST request to "/v1/characters"
    """
    {"name": "C3PO"}
    """
    Then the response status should be 201
    And the response body should contain "payload"
    And the JSON at path "payload.name" should be "C3PO"

  Scenario: Test DBObjectMixin GET object
    When I make a GET request to "/v1/characters/1"
    Then the response status should be 200
    And the response body should contain "payload"
    And the JSON at path "payload.id" should be 1

  Scenario: Test DBObjectMixin PUT object
    When I make a PUT request to "/v1/characters/1"
    """
    {"name": "Obe Wan Kenobe", "id": 1, "created_at": "2017-01-01T10:00:00"}
    """
    Then the JSON should be
    """
    {"payload": {"name": "Obe Wan Kenobe", "id": 1, "created_at": "2017-01-01T10:00:00"}}
    """
    And the response status should be 200

  Scenario: Test DBObjectMixin DELETE object
    When I make a DELETE request to "/v1/characters/1"
    Then the response status should be 204
    When I make a GET request to "/v1/characters/1"
    Then the response status should be 404
