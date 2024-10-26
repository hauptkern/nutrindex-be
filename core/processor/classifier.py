class NutriScore:
    def __init__(self):
        self.energy_points = 0
        self.sugars_points = 0
        self.saturated_fat_points = 0
        self.sodium_points = 0
        self.fruits_veg_nuts_points = 0
        self.fiber_points = 0
        self.protein_points = 0
        self.total_score = 0

    def calculate_energy_points(self, energy_kcal):
        if energy_kcal <= 80:
            self.energy_points = 0
        elif energy_kcal <= 160:
            self.energy_points = 1
        elif energy_kcal <= 240:
            self.energy_points = 2
        elif energy_kcal <= 320:
            self.energy_points = 3
        elif energy_kcal <= 400:
            self.energy_points = 4
        elif energy_kcal <= 480:
            self.energy_points = 5
        elif energy_kcal <= 560:
            self.energy_points = 6
        elif energy_kcal <= 640:
            self.energy_points = 7
        elif energy_kcal <= 720:
            self.energy_points = 8
        elif energy_kcal <= 800:
            self.energy_points = 9
        else:
            self.energy_points = 10

    def calculate_sugars_points(self, sugars_g):
        if sugars_g <= 4.5:
            self.sugars_points = 0
        elif sugars_g <= 9:
            self.sugars_points = 1
        elif sugars_g <= 13.5:
            self.sugars_points = 2
        elif sugars_g <= 18:
            self.sugars_points = 3
        elif sugars_g <= 22.5:
            self.sugars_points = 4
        elif sugars_g <= 27:
            self.sugars_points = 5
        elif sugars_g <= 31:
            self.sugars_points = 6
        elif sugars_g <= 36:
            self.sugars_points = 7
        elif sugars_g <= 40:
            self.sugars_points = 8
        elif sugars_g <= 45:
            self.sugars_points = 9
        else:
            self.sugars_points = 10

    def calculate_saturated_fat_points(self, saturated_fat_g):
        if saturated_fat_g <= 1:
            self.saturated_fat_points = 0
        elif saturated_fat_g <= 2:
            self.saturated_fat_points = 1
        elif saturated_fat_g <= 3:
            self.saturated_fat_points = 2
        elif saturated_fat_g <= 4:
            self.saturated_fat_points = 3
        elif saturated_fat_g <= 5:
            self.saturated_fat_points = 4
        elif saturated_fat_g <= 6:
            self.saturated_fat_points = 5
        elif saturated_fat_g <= 7:
            self.saturated_fat_points = 6
        elif saturated_fat_g <= 8:
            self.saturated_fat_points = 7
        elif saturated_fat_g <= 9:
            self.saturated_fat_points = 8
        elif saturated_fat_g <= 10:
            self.saturated_fat_points = 9
        else:
            self.saturated_fat_points = 10

    def calculate_sodium_points(self, sodium_mg):
        if sodium_mg <= 90:
            self.sodium_points = 0
        elif sodium_mg <= 180:
            self.sodium_points = 1
        elif sodium_mg <= 270:
            self.sodium_points = 2
        elif sodium_mg <= 360:
            self.sodium_points = 3
        elif sodium_mg <= 450:
            self.sodium_points = 4
        elif sodium_mg <= 540:
            self.sodium_points = 5
        elif sodium_mg <= 630:
            self.sodium_points = 6
        elif sodium_mg <= 720:
            self.sodium_points = 7
        elif sodium_mg <= 810:
            self.sodium_points = 8
        elif sodium_mg <= 900:
            self.sodium_points = 9
        else:
            self.sodium_points = 10

    def calculate_fruits_veg_nuts_points(self, fruits_veg_nuts_percent):
        if fruits_veg_nuts_percent <= 40:
            self.fruits_veg_nuts_points = 0
        elif fruits_veg_nuts_percent <= 60:
            self.fruits_veg_nuts_points = 1
        elif fruits_veg_nuts_percent <= 80:
            self.fruits_veg_nuts_points = 2
        else:
            self.fruits_veg_nuts_points = 5

    def calculate_fiber_points(self, fiber_g):
        if fiber_g <= 0.9:
            self.fiber_points = 0
        elif fiber_g <= 1.9:
            self.fiber_points = 1
        elif fiber_g <= 2.8:
            self.fiber_points = 2
        elif fiber_g <= 3.4:
            self.fiber_points = 3
        elif fiber_g <= 4.7:
            self.fiber_points = 4
        else:
            self.fiber_points = 5

    def calculate_protein_points(self, protein_g):
        if protein_g <= 1.6:
            self.protein_points = 0
        elif protein_g <= 3.2:
            self.protein_points = 1
        elif protein_g <= 4.8:
            self.protein_points = 2
        elif protein_g <= 6.4:
            self.protein_points = 3
        elif protein_g <= 8.0:
            self.protein_points = 4
        else:
            self.protein_points = 5

    def calculate_score(self):
        negative_points = (self.energy_points + self.sugars_points +
                           self.saturated_fat_points + self.sodium_points)
        positive_points = (self.fruits_veg_nuts_points + self.fiber_points +
                           self.protein_points)
        if negative_points >= 11 and self.fruits_veg_nuts_points < 5:
            self.total_score = negative_points - self.fruits_veg_nuts_points - self.fiber_points
        else:
            self.total_score = negative_points - positive_points

    def get_nutri_score(self):
        if self.total_score <= -1:
            return 'A'
        elif self.total_score <= 2:
            return 'B'
        elif self.total_score <= 10:
            return 'C'
        elif self.total_score <= 18:
            return 'D'
        else:
            return 'E'

    def calculate_nutri_score(self, energy_kcal, sugars_g, saturated_fat_g,
                              sodium_mg, fruits_veg_nuts_percent, fiber_g, protein_g):
        self.calculate_energy_points(energy_kcal)
        self.calculate_sugars_points(sugars_g)
        self.calculate_saturated_fat_points(saturated_fat_g)
        self.calculate_sodium_points(sodium_mg)
        self.calculate_fruits_veg_nuts_points(fruits_veg_nuts_percent)
        self.calculate_fiber_points(fiber_g)
        self.calculate_protein_points(protein_g)
        self.calculate_score()
        return self.get_nutri_score()
