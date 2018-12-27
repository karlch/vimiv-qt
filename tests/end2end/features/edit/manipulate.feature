Feature: Manipulate an image.

    Scenario: Set brightness value
        Given I open any image
        When I enter manipulate mode
        And I run brightness --value=10
        Then The brightness value should be 10

    Scenario: Set contrast value
        Given I open any image
        When I enter manipulate mode
        And I run contrast --value=10
        Then The contrast value should be 10

    Scenario: Reset manipulation values on discard
        Given I open any image
        When I enter manipulate mode
        And I run brightness --value=10
        And I run discard
        Then The brightness value should be 0
