# Import porzebnych bibliotek
from simpful import *
import random
import queue

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
    P2 = TriangleFuzzySet(0, 0.5, 0.8, term="medium")
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
    def __init__(self, name="", green=False, paired=set()):
        self.name = name
        # Przypisanie systemu rozmytego
        self.fs = create_FS()
        # Stan swiatel (True = zielone, False = czerwone)
        self.state = green
        # Kolejka oczekujacych na przejazd
        self.que = queue.Queue()
        # Liczba samochodow oczekujacych na przejazd
        self.cars = 0
        # Czas od ostatniego zielonego dla kierunku
        self.time = 0
        # Aktualny priorytet dla kierunku (wartosci od 0 do 1)
        self.priority = 0
        # Kierunek sparowany, na ktorym jednoczesnie tez moze byc zielone
        self.paired = paired
        # Pary id-czas oczekiwania samochodow oczekujacych na przejazd
        self.active_cars = {}
        # Pary id-czas oczekiwania samochodow, ktore przejechaly przez skrzyzowanie
        self.passed_cars = {}
        # Sredni czas oczekiwania samochodu na przejazd przez skrzyzowanie na danym kierunku
        self.mwt = 0

    # Procedura obliczajaca aktualny priorytet dla kierunku jazdy
    def calculate_priority(self):
        if self.cars == 0:
            self.priority = 0
        else:
            self.fs.set_variable("number_of_cars", self.cars)
            self.fs.set_variable("waiting_time", self.time)
            self.priority = self.fs.inference()["priority"]

    # Procedura obliczajaca liczbe samochodow oczekujacych z rozmiaru kolejki
    def number_of_cars(self):
        self.cars = self.que.qsize()

# Inicjalizacja skrzyzowania
dirA1 = Direction("A-left", False, {"A-forward", "A-right", "B-right", "C-left", "D-right"})
dirA2 = Direction("A-forward", True, {"A-left", "A-right", "C-forward", "C-right", "D-right"})
dirA3 = Direction("A-right", True, {"A-left", "A-forward", "B-left", "B-forward", "B-right", "C-forward", "C-right", "D-left", "D-right"})
dirB1 = Direction("B-left", False, {"B-forward", "B-right", "C-right", "D-left", "A-right"})
dirB2 = Direction("B-forward", False, {"B-left", "B-right", "D-forward", "D-right", "A-right"})
dirB3 = Direction("B-right", False, {"B-left", "B-forward", "C-left", "C-forward", "C-right", "D-forward", "D-right", "A-left", "A-right"})
dirC1 = Direction("C-left", False, {"C-forward", "C-right", "D-right", "A-left", "B-right"})
dirC2 = Direction("C-forward", True, {"C-left", "C-right", "A-forward", "A-right", "B-right"})
dirC3 = Direction("C-right", True, {"C-left", "C-forward", "D-left", "D-forward", "D-right", "A-forward", "A-right", "B-left", "B-right"})
dirD1 = Direction("D-left", False, {"D-forward", "D-right", "A-right", "B-left", "C-right"})
dirD2 = Direction("D-forward", False, {"D-left", "D-right", "B-forward", "B-right", "C-right"})
dirD3 = Direction("D-right", False, {"D-left", "D-forward", "A-left", "A-forward", "A-right", "B-forward", "B-right", "C-left", "C-right"})

crossroad = [dirA1, dirA2, dirA3, dirB1, dirB2, dirB3, dirC1, dirC2, dirC3, dirD1, dirD2, dirD3]

# Parametr okreslajacy minimalna liczbe samochodow ktore na sekunde (iteracje) moga wjechac na skrzyzowanie
min_cars = 0
# Parametr okreslajacy maksymalna liczbe samochodow ktore na sekunde (iteracje) moga wjechac na skrzyzowanie
max_cars = 6
# Czas trwania zmiany swiatel (w sekundach = iteracjach)
light_duration = 15
# Inicjalizacja id samochodow
id_counter = 0

# Procedura zamiany aktywnego samochodu w taki, ktory przejechal juz skrzyzowanie
def move_car(dict1, dict2, key):
    temp = dict1.pop(key)
    dict2[key] = temp


# Petla symulujaca skrzyzowanie i testujaca sterownik
for i in range(450):
    # Pojawienie sie nowych samochodow na skrzyzowaniu
    m = random.randint(min_cars, max_cars)
    for j in range(m):
        new_car_id = id_counter
        new_car_dir = random.randint(0, len(crossroad)-1)
        crossroad[new_car_dir].que.put(new_car_id)
        crossroad[new_car_dir].active_cars[new_car_id] = 0
        crossroad[new_car_dir].number_of_cars()
        id_counter += 1
    # Obsluga poszczegolnych kierunkow ruchu
    for dir in crossroad:
        # Jesli jest czerwone, to rosnie czas oczekiwania
        if dir.state == False:
            dir.time += 1
        # Jesli jest zielone i sa jakies oczekujace skrzyzowanie, przejezdza jeden samochod na kierunek
        else:
            if dir.cars > 0:
                passed_id = dir.que.get()
                move_car(dir.active_cars, dir.passed_cars, passed_id)
                dir.number_of_cars()
        # Obliczenie zaktualizowanego priorytetu
        dir.calculate_priority()
        # Wszystkim oczekujacym samochodm wydluza sie czas oczekiwania
        for car in dir.active_cars:
            dir.active_cars[car] += 1
    # Zmiana cyklu swiatel
    if i % light_duration == 0:
        print("---NEW CYCLE---")
        chosen = []
        # Wybor kierunku o najwyzszym priorytecie
        priorities = sorted(crossroad, key=lambda dir: dir.priority)
        chosen.append(priorities[-1].name)
        clean = priorities[-1].paired
        # Wybor kierunkow bezkolizyjnych w kolejnosci priorytetu
        for j in range(len(priorities)-2, 0, -1):
            if priorities[j].name in clean:
                chosen.append(priorities[j].name)
                new_clean = clean.intersection(priorities[j].paired)
                clean = new_clean
        chosen_set = set(chosen)
        print(chosen)
        # Ustawienie nowego stanu sygnalizacji swietlnej
        for dir in crossroad:
            # Domyslnie czerwone
            dir.state = False
            # Zielone dla kierunku o najwyzszym priorytecie i kierunkow dla niego bezkolizyjnych
            if dir.name in chosen_set:
                dir.state = True
                dir.time = 0
    # Wypisanie stanu skrzyzowania w danej iteracji
    print("-----Iteration: ", i, ", new cars: ", m, "-----")
    for dir in crossroad:
        print(dir.name, " --- cars: ", dir.cars, ", waiting time: ", dir.time, ", priority: ", dir.priority, ", green: ", dir.state)

global_counter = 0
global_time_sum = 0

# Obliczenie sredniego czasu oczekiwania dla kierunku
for dir in crossroad:
    counter = 0
    time_sum = 0
    for id in dir.active_cars:
        time_sum += dir.active_cars[id]
        counter += 1
    for id in dir.passed_cars:
        time_sum += dir.passed_cars[id]
        counter += 1
    global_counter += counter
    global_time_sum += time_sum
    dir.mwt = time_sum/counter

# Obliczenie globalnego czasu oczekiwania dla calego skrzyzowania
global_mwt = global_time_sum/global_counter

# Statystyki koncowe - liczba samochodow, jakie przejechaly przez skrzyzowanie z poszczegolnych kierunkow
for dir in crossroad:
    print("Direction ", dir.name, ": ", len(dir.passed_cars), " cars passed, mean waiting time: ", dir.mwt)
print("Global mean waiting time: ", global_mwt)

# Test print
=======
# Import porzebnych bibliotek
from simpful import *
import random
import queue

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
    def __init__(self, name="", green=False, paired=set()):
        self.name = name
        # Przypisanie systemu rozmytego
        self.fs = create_FS()
        # Stan swiatel (True = zielone, False = czerwone)
        self.state = green
        # Kolejka oczekujacych na przejazd
        self.que = queue.Queue()
        # Liczba samochodow oczekujacych na przejazd
        self.cars = 0
        # Czas od ostatniego zielonego dla kierunku
        self.time = 0
        # Aktualny priorytet dla kierunku (wartosci od 0 do 1)
        self.priority = 0
        # Kierunek sparowany, na ktorym jednoczesnie tez moze byc zielone
        self.paired = paired
        # Pary id-czas oczekiwania samochodow oczekujacych na przejazd
        self.active_cars = {}
        # Pary id-czas oczekiwania samochodow, ktore przejechaly przez skrzyzowanie
        self.passed_cars = {}
        # Sredni czas oczekiwania samochodu na przejazd przez skrzyzowanie na danym kierunku
        self.mwt = 0

    # Procedura obliczajaca aktualny priorytet dla kierunku jazdy
    def calculate_priority(self):
        if self.cars == 0:
            self.priority = 0
        else:
            self.fs.set_variable("number_of_cars", self.cars)
            self.fs.set_variable("waiting_time", self.time)
            self.priority = self.fs.inference()["priority"]

    # Procedura obliczajaca liczbe samochodow oczekujacych z rozmiaru kolejki
    def number_of_cars(self):
        self.cars = self.que.qsize()

# Inicjalizacja skrzyzowania
dirA1 = Direction("A-left", False, {"A-forward", "A-right", "B-right", "C-left", "D-right"})
dirA2 = Direction("A-forward", True, {"A-left", "A-right", "C-forward", "C-right", "D-right"})
dirA3 = Direction("A-right", True, {"A-left", "A-forward", "B-left", "B-forward", "B-right", "C-forward", "C-right", "D-left", "D-right"})
dirB1 = Direction("B-left", False, {"B-forward", "B-right", "C-right", "D-left", "A-right"})
dirB2 = Direction("B-forward", False, {"B-left", "B-right", "D-forward", "D-right", "A-right"})
dirB3 = Direction("B-right", False, {"B-left", "B-forward", "C-left", "C-forward", "C-right", "D-forward", "D-right", "A-left", "A-right"})
dirC1 = Direction("C-left", False, {"C-forward", "C-right", "D-right", "A-left", "B-right"})
dirC2 = Direction("C-forward", True, {"C-left", "C-right", "A-forward", "A-right", "B-right"})
dirC3 = Direction("C-right", True, {"C-left", "C-forward", "D-left", "D-forward", "D-right", "A-forward", "A-right", "B-left", "B-right"})
dirD1 = Direction("D-left", False, {"D-forward", "D-right", "A-right", "B-left", "C-right"})
dirD2 = Direction("D-forward", False, {"D-left", "D-right", "B-forward", "B-right", "C-right"})
dirD3 = Direction("D-right", False, {"D-left", "D-forward", "A-left", "A-forward", "A-right", "B-forward", "B-right", "C-left", "C-right"})

crossroad = [dirA1, dirA2, dirA3, dirB1, dirB2, dirB3, dirC1, dirC2, dirC3, dirD1, dirD2, dirD3]

# Parametr okreslajacy minimalna liczbe samochodow ktore na sekunde (iteracje) moga wjechac na skrzyzowanie
min_cars = 0
# Parametr okreslajacy maksymalna liczbe samochodow ktore na sekunde (iteracje) moga wjechac na skrzyzowanie
max_cars = 6
# Czas trwania zmiany swiatel (w sekundach = iteracjach)
light_duration = 15
# Inicjalizacja id samochodow
id_counter = 0

# Procedura zamiany aktywnego samochodu w taki, ktory przejechal juz skrzyzowanie
def move_car(dict1, dict2, key):
    temp = dict1.pop(key)
    dict2[key] = temp


# Petla symulujaca skrzyzowanie i testujaca sterownik
for i in range(450):
    # Pojawienie sie nowych samochodow na skrzyzowaniu
    m = random.randint(min_cars, max_cars)
    for j in range(m):
        new_car_id = id_counter
        new_car_dir = random.randint(0, len(crossroad)-1)
        crossroad[new_car_dir].que.put(new_car_id)
        crossroad[new_car_dir].active_cars[new_car_id] = 0
        crossroad[new_car_dir].number_of_cars()
        id_counter += 1
    # Obsluga poszczegolnych kierunkow ruchu
    for dir in crossroad:
        # Jesli jest czerwone, to rosnie czas oczekiwania
        if dir.state == False:
            dir.time += 1
        # Jesli jest zielone i sa jakies oczekujace skrzyzowanie, przejezdza jeden samochod na kierunek
        else:
            if dir.cars > 0:
                passed_id = dir.que.get()
                move_car(dir.active_cars, dir.passed_cars, passed_id)
                dir.number_of_cars()
        # Obliczenie zaktualizowanego priorytetu
        dir.calculate_priority()
        # Wszystkim oczekujacym samochodm wydluza sie czas oczekiwania
        for car in dir.active_cars:
            dir.active_cars[car] += 1
    # Zmiana cyklu swiatel
    if i % light_duration == 0:
        print("---NEW CYCLE---")
        chosen = []
        # Wybor kierunku o najwyzszym priorytecie
        priorities = sorted(crossroad, key=lambda dir: dir.priority)
        chosen.append(priorities[-1].name)
        clean = priorities[-1].paired
        # Wybor kierunkow bezkolizyjnych w kolejnosci priorytetu
        for j in range(len(priorities)-2, 0, -1):
            if priorities[j].name in clean:
                chosen.append(priorities[j].name)
                new_clean = clean.intersection(priorities[j].paired)
                clean = new_clean
        chosen_set = set(chosen)
        print(chosen)
        # Ustawienie nowego stanu sygnalizacji swietlnej
        for dir in crossroad:
            # Domyslnie czerwone
            dir.state = False
            # Zielone dla kierunku o najwyzszym priorytecie i kierunkow dla niego bezkolizyjnych
            if dir.name in chosen_set:
                dir.state = True
                dir.time = 0
    # Wypisanie stanu skrzyzowania w danej iteracji
    print("-----Iteration: ", i, ", new cars: ", m, "-----")
    for dir in crossroad:
        print(dir.name, " --- cars: ", dir.cars, ", waiting time: ", dir.time, ", priority: ", dir.priority, ", green: ", dir.state)

global_counter = 0
global_time_sum = 0

# Obliczenie sredniego czasu oczekiwania dla kierunku
for dir in crossroad:
    counter = 0
    time_sum = 0
    for id in dir.active_cars:
        time_sum += dir.active_cars[id]
        counter += 1
    for id in dir.passed_cars:
        time_sum += dir.passed_cars[id]
        counter += 1
    global_counter += counter
    global_time_sum += time_sum
    dir.mwt = time_sum/counter

# Obliczenie globalnego czasu oczekiwania dla calego skrzyzowania
global_mwt = global_time_sum/global_counter

# Statystyki koncowe - liczba samochodow, jakie przejechaly przez skrzyzowanie z poszczegolnych kierunkow
for dir in crossroad:
    print("Direction ", dir.name, ": ", len(dir.passed_cars), " cars passed, mean waiting time: ", dir.mwt)
print("Global mean waiting time: ", global_mwt)

# Test print
#print(dirA.active_cars)