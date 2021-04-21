Feature: Manipulate an image.

    Background:
        Given I open any image

    Scenario: Set value of current manipulation
        When I enter manipulate mode
        And I run goto 10
        Then The current value should be 10

    Scenario: Set value of current manipulation via keybinding
        When I enter manipulate mode
        And I press '10gg'
        Then The current value should be 10

    Scenario: Set value using increase
        When I enter manipulate mode
        And I run increase 10
        Then The current value should be 10

    Scenario: Set value using increase keybinding
        When I enter manipulate mode
        And I press '10k'
        Then The current value should be 10

    Scenario: Set value to zero via keybinding
        When I enter manipulate mode
        And I run goto 10
        And I press '0gg'
        Then The current value should be 0

    Scenario: Focus next manipulation
        When I enter manipulate mode
        And I run next
        Then the current manipulation should be contrast

    Scenario: Do not reset value on focus
        When I enter manipulate mode
        And I run goto 10
        And I run 2next
        Then the current manipulation should be brightness
        And the current value should be 10

    Scenario: Focus next manipulation tab
        When I enter manipulate mode
        And I run next-tab
        Then the current manipulation should be hue

    Scenario: Store manipulation change
        When I enter manipulate mode
        And I apply any manipulation
        And I run next-tab
        Then there should be 1 stored changes

    Scenario: Store multiple manipulation changes
        When I enter manipulate mode
        And I apply any manipulation
        And I run next-tab
        And I apply any manipulation
        And I run next-tab
        Then there should be 2 stored changes

    Scenario: Reset manipulation values on discard
        When I enter manipulate mode
        And I apply any manipulation
        And I run discard
        Then The current value should be 0

    Scenario: Reset manipulation changes after accepting them
        When I enter manipulate mode
        And I apply any manipulation
        And I run accept
        Then there should be 0 stored changes

    Scenario: Do not allow entering manipulate when read_only is active
        When I run set read_only true
        And I enter manipulate mode
        Then the message
            'Manipulate mode is disabled due to read-only being active'
            should be displayed
        And the mode should be image
