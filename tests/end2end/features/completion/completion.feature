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
        When I enter command mode with "open "
        Then the completion model should be path

    Scenario: Using setting completion.
        Given I open any directory
        When I enter command mode with "set "
        Then the completion model should be settings

    Scenario: Using setting option completion.
        Given I open any directory
        When I enter command mode with "set shuffle"
        Then the completion model should be settings_option

    Scenario: Using trash completion.
        Given I open any directory
        When I enter command mode with "undelete "
        Then the completion model should be trash

    Scenario: Crash on path completion with non-existent directory
        Given I open any directory
        When I enter command mode with "open /foo/bar/baz"
        Then no crash should happen

    Scenario: Reset completions when leaving command mode
        Given I open any directory
        When I run command
        And I run complete
        And I run leave-commandline
        Then no completion should be selected

    Scenario: Crash when completing on entered number
        Given I open any directory
        When I enter command mode with "2"
        And I run complete
        Then no crash should happen

    Scenario: Do not use path completion on open-
        Given I open any directory
        When I enter command mode with "open-"
        Then the completion model should be command

    Scenario: Do not show hidden setting in completion.
        Given I open any directory
        When I enter command mode with "set history_li"
        And I run complete
        Then no completion should be selected

    Scenario: Escape path with spaces upon completion
        Given I open any directory
        When I run !mkdir 'path with spaces'
        And I wait for the command to complete
        And I enter command mode with "open pat"
        And I run complete
        And I activate the command line
        Then the working directory should be path with spaces

    Scenario: Update setting completion with newest value
        Given I open any directory
        When I run set slideshow.delay 42
        And I enter command mode with "set slideshow.delay"
        And I run complete
        Then a possible completion should contain 42
