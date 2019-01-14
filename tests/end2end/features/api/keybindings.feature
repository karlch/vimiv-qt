Feature: Bind and unbind keybindings.

    Scenario: Bind in library mode
        Given I open any directory
        When I run bind tmp1 test
        Then the keybinding tmp1 should exist for mode library

    Scenario: Bind in global mode
        Given I open any directory
        When I run bind tmp2 test --mode=global
        Then the keybinding tmp2 should exist for mode global

    Scenario: Bind and unbind command
        Given I open any directory
        When I run bind tmp3 test
        And I run unbind tmp3
        Then the keybinding tmp3 should not exist for mode library
