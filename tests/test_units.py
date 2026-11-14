from core.units import circumference_from_flat, body_from_garment


def test_flat_forty_is_eighty_round():
    assert circumference_from_flat(40) == 80


def test_eighty_round_with_eight_ease_is_seventy_two_body():
    assert body_from_garment(80, 8) == 72


def test_negative_ease_makes_body_bigger_than_garment():
    # stretchy leggings: the body is bigger than the garment lying flat
    assert body_from_garment(60, -8) == 68