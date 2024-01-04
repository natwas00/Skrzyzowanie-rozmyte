# Import porzebnych bibliotek
from simpful import *
import random

# Tworzenie systemu rozmytego - wlasciwy sterownik
def create_FS():
    FS = FuzzySystem()

    # Zamodelowanie zmiennej lingwistycznej "liczba samochodow"
    C1 = TrapezoidFuzzySet(0, 0, 4, 8, term="low")
    C2 = TriangleFuzzySet(4, 8, 12, term="medium")
    C3 = TriangleFuzzySet(8, 12, 32, term="high")
    C4 = TriangleFuzzySet(12, 32, 32, term="very_high")
    FS.add_linguistic_variable("number_of_cars", LinguisticVariable([C1, C2, C3, C4], universe_of_discourse=[0, 32]))

    # Zamodelowanie zmiennej lingwistycznej "czas od poprzedniego zielonego"
    T1 = TrapezoidFuzzySet(0, 0, 15, 45, term="short")
    T2 = TriangleFuzzySet(15, 45, 75, term="medium")
    T3 = TrapezoidFuzzySet(45, 75, 150, 150, term="long")
    FS.add_linguistic_variable("waiting_time", LinguisticVariable([T1, T2, T3], universe_of_discourse=[0, 150]))

    # Zamodelowanie sterujacej zmiennej lingwistycznej "priorytet"
    P1 = TriangleFuzzySet(0, 0, 0.5, term="low")
    P2 = TriangleFuzzySet(0, 0.5, 1, term="medium")
    P3 = TriangleFuzzySet(0.5, 0.8, 1, term="high")
    P4 = TriangleFuzzySet(0.8, 1, 1, term="very_high")
    FS.add_linguistic_variable("priority", LinguisticVariable([P1, P2, P3, P4], universe_of_discourse=[0, 1]))

    # Zdefiniowanie zestawu regul
    FS.add_rules([

        "IF (number_of_cars IS low) AND (waiting_time IS short) THEN (priority IS low)",

        "IF (number_of_cars IS low) AND (waiting_time IS medium) THEN (priority IS medium)",

        "IF (number_of_cars IS medium) THEN (priority IS medium)",

        "IF (number_of_cars IS high) AND (waiting_time IS short) THEN (priority IS medium)",

        "IF (number_of_cars IS high) AND (waiting_time IS medium) THEN (priority IS high)",

        "IF (number_of_cars IS very_high) OR (waiting_time IS long) THEN (priority IS very_high)"

    ])

    # Zwraca system rozmyty, ktory moze byc przypisany do konkretnego kierunku ruchu
    return FS

# Klasa "Kierunek" przechowujaca informacje o stanie danego kierunku ruchu oraz jego system rozmyty
class Direction:
    # constructor function
    def __init__(self, name="", green=False, paired=""):
        self.name = name
        # Przypisanie systemu rozmytego
        self.fs = create_FS()
        # Stan swiatel (True = zielone, False = czerwone)
        self.state = green
        # Liczba samochodow oczekujacych na przejazd
        self.cars = 0
        # Czas od ostatniego zielonego dla kierunku
        self.time = 0
        # Aktualny priorytet dla kierunku (wartosci od 0 do 1)
        self.priority = 0
        # Kierunek sparowany, na ktorym jednoczesnie tez moze byc zielone
        self.paired = paired
        # Licznik samochodow, ktore przejechaly przez skrzyzowanie z danego kierunku
        self.passed = 0

    # Procedura obliczajaca aktualny priorytet dla kierunku jazdy
    def calculate_priority(self):
        self.fs.set_variable("number_of_cars", self.cars)
        self.fs.set_variable("waiting_time", self.time)
        self.priority = self.fs.inference()["priority"]

# Inicjalizacja skrzyzowania
dirA = Direction("A", True, "C")
dirB = Direction("B", False, "D")
dirC = Direction("C", True, "A")
dirD = Direction("D", False, "B")

crossroad = [dirA, dirB, dirC, dirD]

# Parametr okreslajacy minimalna liczbe samochodow ktore na sekunde (iteracje) moga wjechac na skrzyzowanie
min_cars = 0
# Parametr okreslajacy maksymalna liczbe samochodow ktore na sekunde (iteracje) moga wjechac na skrzyzowanie
max_cars = 4
# Czas trwania zmiany swiatel (w sekundach = iteracjach)
light_duration = 15

# Petla symulujaca skrzyzowanie i testujaca sterownik
for i in range(450):
    # Pojawienie sie nowych samochodow na skrzyzowaniu
    m = random.randint(min_cars, max_cars)
    for j in range(m):
        new_car = random.randint(0, 3)
        crossroad[new_car].cars += 1
    # Obsluga poszczegolnych kierunkow ruchu
    for dir in crossroad:
        # Jesli jest czerwone, to rosnie czas oczekiwania
        if dir.state == False:
            dir.time += 1
        # Jesli jest zielone i sa jakies oczekujace skrzyzowanie, przejezdza jeden samochod na kierunek
        else:
            if dir.cars > 0:
                dir.cars = dir.cars - 1
                dir.passed += 1
        # Obliczenie zaktualizowanego priorytetu
        dir.calculate_priority()
    # Zmiana cyklu swiatel
    if i % light_duration == 0:
        print("---NEW CYCLE---")
        # Wybor kierunku o najwyzszym priorytecie
        priorities = sorted(crossroad, key=lambda dir: dir.priority)
        max_p = priorities[-1]
        # Ustawienie nowego stanu sygnalizacji swietlnej
        for dir in crossroad:
            # Domyslnie czerwone
            dir.state = False
            # Zielone dla kierunku o najwyzszym priorytecie
            if dir == max_p:
                dir.state = True
                dir.time = 0
            # Zielone dla kierunku sparowanego z tym o najwyzszym priorytecie
            elif dir.name == max_p.paired:
                dir.state = True
                dir.time = 0
    # Wypisanie stanu skrzyzowania w danej iteracji
    print("Iteration: ", i, " new cars: ", m)
    print("A -- cars: ", dirA.cars, " waiting_time: ", dirA.time, " priority: ", dirA.priority, " green: ", dirA.state)
    print("B -- cars: ", dirB.cars, " waiting_time: ", dirB.time, " priority: ", dirB.priority, " green: ", dirB.state)
    print("C -- cars: ", dirC.cars, " waiting_time: ", dirC.time, " priority: ", dirC.priority, " green: ", dirC.state)
    print("D -- cars: ", dirD.cars, " waiting_time: ", dirD.time, " priority: ", dirD.priority, " green: ", dirD.state)

# Statystyki koncowe - liczba samochodow, jakie przejechaly przez skrzyzowanie z poszczegolnych kierunkow
print("Passed cars -- A: ", dirA.passed, " -- B: ", dirB.passed, " -- C: ", dirC.passed, " --D: ", dirD.passed)
