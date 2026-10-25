def recommend_food(foods, budget=200, preference="Any"):
    """Simple transparent rule-based recommendations for the student project."""
    matching = []
    for food in foods:
        if float(food.get("price", 0)) > float(budget):
            continue
        category = food.get("category", "")
        if preference != "Any" and preference.lower() not in category.lower():
            continue
        matching.append(food)
    return sorted(
        matching,
        key=lambda item: (
            float(item.get("calories", 0)),
            -float(item.get("protein", 0)),
            float(item.get("price", 0)),
        )
    )[:8]


def recommend_healthy_food(foods, budget=200, diet="Any",
                           goal="Balanced", max_calories=700,
                           min_protein=0):
    """Ranks menu items using nutrition estimates, budget, diet and goal."""
    results = []
    for food in foods:
        price = float(food.get("price", 0))
        calories = int(food.get("calories", 0) or 0)
        protein = float(food.get("protein", 0) or 0)
        carbs = float(food.get("carbs", 0) or 0)
        diet_type = food.get("diet_type", "Vegetarian")

        if price > budget or calories > max_calories or protein < min_protein:
            continue
        if diet != "Any":
            if diet == "Vegetarian" and diet_type not in ("Vegetarian", "Vegan"):
                continue
            if diet == "Vegan" and diet_type != "Vegan":
                continue
            if diet == "Egg" and diet_type not in ("Egg", "Vegetarian", "Vegan"):
                continue
            if diet == "Non-vegetarian" and diet_type not in ("Non-vegetarian", "Egg"):
                continue

        if goal == "High protein":
            score = protein * 3 - calories * 0.01
        elif goal == "Lower calorie":
            score = -calories + protein * 1.5
        else:
            score = protein * 2 - abs(calories - 450) * 0.03 - carbs * 0.05

        results.append((score, food))
    results.sort(key=lambda pair: pair[0], reverse=True)
    return [food for _, food in results[:10]]
