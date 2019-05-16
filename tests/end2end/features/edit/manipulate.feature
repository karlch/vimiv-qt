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

    Scenario: Set brightness value from command line
        Given I open any image
        When I enter manipulate mode
        And I run command
        And I press brightness --value=14
        And I activate the command line
        Then The mode should be manipulate
        And The brightness value should be 14

    Scenario: Set brightness value via key binding and count
        Given I open any image
        When I enter manipulate mode
        And I press 20gg
        Then the brightness value should be 20

    Scenario: Set brightness value to zero via key binding and count
        Given I open any image
        When I enter manipulate mode
        And I press 20gg
        And I press 0gg
        Then the brightness value should be 0
