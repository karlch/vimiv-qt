Feature: Write an image to disk

    Scenario Outline: Write image to new path
        Given I open any image
        When I write the image to <name>
        Then the file <name> should exist

        Examples:
            | name          |
            | new_path.jpg  |
            | new_path.png  |
            | new_path.tiff |

    @optional
    Scenario: Write image preserving exif information
        Given I open any image
        When I add exif information
        And I write the image to new_path.jpg
        Then the image new_path.jpg should contain exif information
