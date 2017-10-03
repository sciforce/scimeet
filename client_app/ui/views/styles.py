

# TODO: refactor fn calls
def rgb_to_kivy(rgb):
    return [
        float(rgb[0]) / 255,  # red
        float(rgb[1]) / 255,  # green
        float(rgb[2]) / 255,  # blue
        float(rgb[3])         # alpha
    ]


def image(image_name):
    return '{}/{}.png'.format(Globals.IMAGES_DIR, image_name)


class Globals:
    FONT_DIR = "ui/res/fonts/"
    IMAGES_DIR = "ui/res/img/"


class GlobalStyle:

    standard_caption_font = "{}exo2_light.ttf".format(Globals.FONT_DIR)
    semibold_caption_font = "{}exo2_semibold.ttf".format(Globals.FONT_DIR)
    extrabold_caption_font = "{}exo2_extrabold.ttf".format(Globals.FONT_DIR)

    app_screen_size = (800, 600)
    standard_button_size = ("80dp", "80dp")
    standard_menu_item_size = standard_button_size[0]

    standard_caption_font_size = "22sp"
    big_caption_font_size = "30sp"
    extra_big_caption_font_size = "50sp"
    huge_caption_font_size = "130sp"
    extra_huge_caption_font_size = "190sp"

    empty_background_color = rgb_to_kivy([0, 0, 0, 0])
    free_room_background_color = rgb_to_kivy([81, 183, 73, 0.3])
    menu_background_color = rgb_to_kivy([34, 41, 66, 0.8])
    error_screen_background_color = rgb_to_kivy([220, 33, 39, 0.8])

    weekly_item_available_color = rgb_to_kivy([14, 21, 46, 0.8])
    weekly_item_unavailable_color = rgb_to_kivy([255, 255, 255, 0.8])
    weekly_item_current_day_color = rgb_to_kivy([146, 164, 232, 0.8])

    daily_available_meeting_color = rgb_to_kivy([146, 164, 232, 0.8])
    daily_unavailable_meeting_color = rgb_to_kivy([255, 255, 255, 0.8])

    list_item_selected_color = rgb_to_kivy([23, 23, 63, 0.8])
    list_item_deselected_color = rgb_to_kivy([49, 49, 90, 0.8])

    blue = rgb_to_kivy([164, 189, 252, 0.8])
    green = rgb_to_kivy([122, 231, 191, 0.8])
    purple = rgb_to_kivy([219, 173, 255, 0.8])
    red = rgb_to_kivy([255, 136, 124, 0.8])
    yellow = rgb_to_kivy([251, 215, 91, 0.8])
    orange = rgb_to_kivy([255, 184, 120, 0.8])
    turquoise = rgb_to_kivy([70, 214, 219, 0.8])
    grey = rgb_to_kivy([225, 225, 225, 0.8])
    bold_blue = rgb_to_kivy([84, 132, 236, 0.8])
    bold_green = rgb_to_kivy([81, 183, 73, 0.8])
    bold_red = rgb_to_kivy([220, 33, 39, 0.8])
