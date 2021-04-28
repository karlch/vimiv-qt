Feature: Miscellaneous features connected to the library

    Background:
        Given I open a directory with 2 paths

    Scenario: Hide hidden files
        When I create the directory '.hidden'
        And I reload the library
        Then the library should contain 2 paths

    Scenario: Show hidden files
        When I create the directory '.hidden'
        And I reload the library
        And I run set library.show_hidden true
        Then the library should contain 3 paths
        # .hidden is placed in front of the current selection
        And the library row should be 2
