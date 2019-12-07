Feature: Bind and unbind keybindings.

    Scenario: Bind in library mode
        Given I open any directory
        When I run bind ZX test
        Then the keybinding ZX should exist for mode library

    Scenario: Bind in global mode
        Given I open any directory
        When I run bind ZX test --mode=global
        Then the keybinding ZX should exist for mode image
        And the keybinding ZX should exist for mode library
        And the keybinding ZX should exist for mode thumbnail

    Scenario: Bind and unbind command
        Given I open any directory
        When I run bind ZX test
        And I run unbind ZX
        Then the keybinding ZX should not exist for mode library
