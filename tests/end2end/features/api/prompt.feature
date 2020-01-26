Feature: Prompt the user for a question

    Scenario Outline: Ask a question and answer it
        Given I open any directory
        And I ask a question and press <key>
        Then I expect <answer> as answer

        Examples:
            | key        | answer |
            | y          | true   |
            | n          | false  |
            | <return>   | false  |
            | <escape>   | none   |
