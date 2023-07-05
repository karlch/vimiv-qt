Feature: Ensure the application works correctly without optional dependencies

    @nometadata
    Scenario: No metadata command
        Given I open any image
        When I run metadata
        Then the message
            'metadata: unknown command for mode image'
            should be displayed
