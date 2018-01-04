Feature: Using completion.

    Scenario: Using library command completion.
        Given I open any directory
        When I run command
        Then the completion model should be command
        And the model mode should be library

    Scenario: Using image command completion.
        Given I open any image
        When I run command
        Then the completion model should be command
        And the model mode should be image

    Scenario: Using path completion.
        Given I open any directory
        When I enter command mode with open
        Then the completion model should be path

    Scenario: Using setting completion.
        Given I open any directory
        When I enter command mode with set
        Then the completion model should be settings

    Scenario: Crash on path completion with non-existent directory
        Given I open any directory
        When I enter command mode with open /foo/bar/baz
        Then no crash should happen

    Scenario: Reset completions when leaving command mode
        Given I open any directory
        When I run command
        And I run complete
        And I run leave-commandline
        Then no completion should be selected
