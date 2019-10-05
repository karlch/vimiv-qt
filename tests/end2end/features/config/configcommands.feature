Feature: Miscellaneous commands related to the config

    Scenario: Toggle boolean setting
        Given I start vimiv
        When I run set completion.fuzzy!
        Then the boolean setting 'completion.fuzzy' should be 'true'

    Scenario: Toggle boolean setting twice
        Given I start vimiv
        When I run set completion.fuzzy!
        And I run set completion.fuzzy!
        Then the boolean setting 'completion.fuzzy' should be 'false'

    Scenario: Reset setting to default value
        Given I start vimiv
        When I run set completion.fuzzy false
        And I run set completion.fuzzy
        Then the boolean setting 'completion.fuzzy' should be 'false'

    Scenario: Do not crash on unknown setting
        Given I start vimiv
        When I run set anything.unknown false
        Then no crash should happen
        And the message
            'set: unknown setting 'anything.unknown''
            should be displayed

    Scenario: Do not crash on unsupported setting operation
        Given I start vimiv
        When I run set completion.fuzzy +10
        Then no crash should happen
        And the message
            'set: 'completion.fuzzy' does not support adding'
            should be displayed

    Scenario: Do not crash on wrong setting value
        Given I start vimiv
        When I run set library.width forty
        Then no crash should happen
        And the message
            'set: Cannot convert 'forty' to Float'
            should be displayed
