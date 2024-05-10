@metadata
Feature: Metadata widget displaying image exif information

    Scenario: Show metadata widget
        Given I open any image
        When I add exif information
        And I run metadata
        Then the metadata widget should be visible
        And the metadata text should contain 'Make'
        And the metadata text should contain 'vimiv-testsuite'
        And the metadata text should contain 'Model'
        And the metadata text should contain 'image-viewer'

    Scenario: Toggle metadata widget
        Given I open any image
        When I run metadata
        And I run metadata
        Then the metadata widget should not be visible

    Scenario: Switch to second metadata key set
        Given I open any image
        When I add exif information
        And I run 2metadata
        Then the metadata widget should be visible
        And the metadata text should contain 'ExposureTime'
        And the metadata text should contain '1/200'

    Scenario: Switch to third metadata key set
        Given I open any image
        When I add exif information
        And I run 3metadata
        Then the metadata widget should be visible
        And the metadata text should contain 'GPSAltitude'
        And the metadata text should contain '1234'

    Scenario: Error message on invalid metadata key set number
        Given I open any image
        When I run 42metadata
        Then the metadata widget should not be visible
        And the message
            'metadata: Invalid key set option 42'
            should be displayed

    Scenario: Switch metadata information upon new image
        Given I open 2 images
        When I add exif information
        And I run metadata
        And I run next
        Then the metadata widget should be visible
        # The new image no longer has any exif information
        And the metadata text should contain 'No matching metadata found'

    Scenario: Display list of valid metadata keys
        Given I open any image
        When I add exif information
        And I run metadata-list-keys
        Then the metadata widget should be visible
        And the metadata text should contain 'Make'
        And the metadata text should contain 'Model'
        And the metadata text should contain 'Copyright'

    Scenario: Print list of valid metadata keys
        Given I open any image
        And I capture output
        When I add exif information
        And I run metadata-list-keys --to-term
        Then the metadata widget should not be visible
        And stdout should contain 'Make'
        And stdout should contain 'Model'
        And stdout should contain 'Copyright'

    Scenario: Do not crash on svg files
        Given I open a vector graphic
        When I run metadata
        Then no crash should happen
        And the metadata text should contain 'No matching metadata found'
