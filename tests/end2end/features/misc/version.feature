Feature: Version command with pop up window.

    Scenario: Display the version pop up.
        Given I start vimiv
        When I run version
        Then the pop up 'vimiv - version' should be displayed

    Scenario: Copy version information to clipboard.
        Given I start vimiv
        When I run version --copy
        Then the clipboard should contain vimiv
