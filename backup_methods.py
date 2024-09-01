def handle_list_stations_command(player_ship, game, args):
    """Handles the list stations command."""
    valid_sort_orders = ['asc', 'des']
    valid_sort_types = ['distance', 'd']
    valid_filters = ['refinery', 'refuelling', 'combined', 'all']

    selected_stations: list = []

    if len(args) == 0:
        for station in game.refuelling_stations:
            print(station.to_string())
        for station in game.refineries:
            print(station.to_string())
        for station in game.combined_stations:
            print(station.to_string())

        return

    elif len(args) == 1:
        if args[0] in valid_sort_orders:
            sort_type = "distance"
            selected_stations: list = game.sort_stations(sort_type, args[0], filter,
                                                   player_ship.position)
        if args[0] in valid_sort_types:
            sort_order = "asc"
            selected_stations: list = game.sort_stations(args[0], sort_order, filter,
                                                   player_ship.position)
        if args[0] in valid_filters:
            sort_order = "asc"
            sort_type = "distance"
            selected_stations = game.sort_stations(sort_type, sort_order,
                                                   args[0],
                                                   player_ship.position)
        else:
            print(
                "Please select at least a valid sort order, type or a filter.")
            print("Valid sort orders: asc, des")
            print("Valid sort types: [distance, d]")
            print("Valid filters: refinery, refuelling, combined, all")
            return

    elif len(args) == 2:
        if args[0] in valid_sort_orders and args[1] in valid_sort_types:
            selected_stations = game.sort_stations(args[1], args[0],
                                                   player_ship.position)
        else:
            print("Please select a valid sort order and type.")
            print("Valid sort orders: asc, des")
            print("Valid sort types: [distance, d]")
            print("Valid filters: refinery, refuelling, combined, all")
            return

    elif len(args) == 3:
        if args[0] in valid_sort_orders and args[
                1] in valid_sort_types and args[2] in valid_filters:
            selected_stations = game.sort_stations(args[1], args[0], args[2],
                                                   player_ship.position)
        else:
            print("Please select a valid sort order, type and filter.")
            print("Valid sort orders: asc, des")
            print("Valid sort types: [distance, d]")
            print("Valid filters: refinery, refuelling, combined, all")
            return

    # elif len(args) >= 4:
    else:
        print(
            "Too many arguments. Please provide a valid sort order, type or filter."
        )
        return

    for station in selected_stations:
        print(station.to_string())


def handle_list_fields_command(player_ship, solar_system, args):
    """Handles the list fields command."""
    valid_sort_types = ['radius', 'asteroids', 'distance', 'r', 'a', 'd']
    valid_sort_orders = ['asc', 'des']

    if len(args) == 0:
        for field in solar_system.asteroid_fields:
            print(field.to_string(player_ship.position))
    elif len(args) == 2:
        sort_order, sort_type = args[0], args[1]
        if sort_order not in valid_sort_orders:
            print("Invalid sort order. Please enter 'asc' or 'des'.")
        if sort_type not in valid_sort_types:
            print(
                "Invalid sort type. Please enter 'radius' (r), 'asteroids'(a), or 'distance'(d)."
            )
            return

        selected_fields = solar_system.sort_fields(sort_order, sort_type,
                                                   player_ship.position)
        for field in selected_fields:
            print(field.to_string(player_ship.position))
