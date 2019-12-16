Feature: Welcome-to-qt command with pop up window

    Scenario: Show welcome pop up
        Given I start vimiv
        When I run welcome-to-qt
        Then the pop up 'vimiv - welcome to qt' should be displayed
