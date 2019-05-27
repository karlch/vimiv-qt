Feature: Plugin system with default plugins

    Scenario: Fail print command without image
        Given I open any directory
        When I enter image mode
        And I run print
        Then the message
             'print: No widget to print'
             should be displayed

    Scenario: Show print dialog
        Given I open any image
        When I run print
        Then the pop up 'Print' should be displayed

    @flaky
    Scenario: Show print preview dialog
        Given I open any image
        When I run print --preview
        Then the pop up 'Print Preview' should be displayed
