Feature: Resize the library.

    Background:
        Given I open any directory

    Scenario: Resize the library when the main window changes width.
        When I resize the window to 400x600
        Then the library width should be 0.3

    Scenario: Increase the library size.
        When I run set library.width +0.1
        Then the library width should be 0.4

    Scenario: Decrease the library size.
        When I run set library.width -0.1
        Then the library width should be 0.2

    Scenario: Decrease to the minimum size.
        When I run set library.width 0
        Then the library width should be 0.05

    Scenario: Increase to maximum size.
        When I run set library.width 1
        Then the library width should be 0.95

    Scenario: Increase and reset to default size.
        When I run set library.width 1
        And I run set library.width
        Then the library width should be 0.3
