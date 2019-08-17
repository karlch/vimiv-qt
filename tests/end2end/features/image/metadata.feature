Feature: Metadata widget displaying image exif information

    Scenario: Show metadata widget
        Given I open any image
        When I run metadata
        Then the metadata widget should be visible

    Scenario: Toggle metadata widget
        Given I open any image
        When I run metadata
        And I run metadata
        Then the metadata widget should not be visible
