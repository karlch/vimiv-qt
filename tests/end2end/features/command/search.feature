Feature: Run search in different modes.

    Scenario: Search in library mode
        Given I open a directory with 5 paths
        When I search for 3
        Then the library row should be 3
        And there should be 1 search matches

    Scenario: Search in image mode
        Given I open 5 images
        When I search for 3
        Then the image should have the index 3
        And there should be 1 search matches

    Scenario: Search in thumbnail mode
        Given I open 5 images
        When I enter thumbnail mode
        And I search for 3
        Then the thumbnail number 3 should be selected
        And there should be 1 search matches

    Scenario: Navigate search results forward
        Given I open a directory with 15 paths
        When I search for 1
        # Matches: _01, _10, _11, _12, _13, _14, _15
        # Current: _01
        And I run 2search-next
        # Move two forward to _11
        Then the library row should be 11
        And there should be 7 search matches

    Scenario: Navigate search results backward
        Given I open a directory with 15 paths
        When I search for 1
        # Matches: _01, _10, _11, _12, _13, _14, _15
        # Current: _01
        And I run search-prev
        # Move backward to _15
        Then the library row should be 15
        And there should be 7 search matches

    Scenario: Navigate search results forward in reverse
        Given I open a directory with 15 paths
        When I search in reverse for 1
        And I run search-next
        Then the library row should be 15
        And there should be 7 search matches

    Scenario: Navigate search results backward in reverse
        Given I open a directory with 15 paths
        When I search in reverse for 1
        And I run search-prev
        Then the library row should be 10
        And there should be 7 search matches

    Scenario: Search using unix-style asterisk pattern matching
        Given I open a directory with 15 paths
        When I search for 1*
        # Matches: 1, 10, 11, 12, 13, 14, 15
        Then there should be 7 search matches

    Scenario: Search using unix-style question mark pattern matching
        Given I open a directory with 15 paths
        When I search for 1?
        # Matches: 10, 11, 12, 13, 14, 15
        Then there should be 6 search matches

    Scenario: Search using unix-style group pattern matching
        Given I open a directory with 15 paths
        When I search for 1[234]
        # Matches: 12, 13, 14
        Then there should be 3 search matches

    Scenario: Reset search when working directory changed
        Given I open a directory with 5 paths
        When I search for 1
        And I run open-selected
        Then there should be 0 search matches

    @flaky
    Scenario: Re-run search when working directory was updated
        Given I open a directory with 5 paths
        When I search for 1
        And I run !cp -r child_01 child_11
        And I wait for the working directory handler
        Then there should be 2 search matches

    Scenario: Crash when searching empty pathlist
        Given I start vimiv
        When I search for *
        Then no crash should happen

    Scenario: Reset search on escape
        Given I open a directory with 5 paths
        When I search for *
        And I press <escape>
        Then there should be 0 search matches
