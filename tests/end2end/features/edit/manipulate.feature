Feature: Manipulate an image.

    Background:
        Given I open any image

    Scenario: Set brightness value
        When I enter manipulate mode
        And I run brightness --value=10
        Then The brightness value should be 10

    Scenario: Set contrast value
        When I enter manipulate mode
        And I run contrast --value=10
        Then The contrast value should be 10

    Scenario: Reset manipulation values on discard
        When I enter manipulate mode
        And I run brightness --value=10
        And I run discard
        Then The brightness value should be 0

    Scenario: Set brightness value from command line
        When I enter manipulate mode
        And I run command
        And I press brightness --value=14
        And I activate the command line
        Then The mode should be manipulate
        And The brightness value should be 14

    Scenario: Set brightness value via key binding and count
        When I enter manipulate mode
        And I press 20gg
        Then the brightness value should be 20

    Scenario: Set brightness value to zero via key binding and count
        When I enter manipulate mode
        And I press 20gg
        And I press 0gg
        Then the brightness value should be 0

    Scenario: Do not reset brightness value on focus
        When I enter manipulate mode
        And I run brightness --value=10
        And I run brightness
        Then the brightness value should be 10
