import pickle


class RegistroJuego():
   #Proporciona datos de una partida grabada  
    #Iterando sobre la instancia  
   # Devuelve valor_dado e índice

    def __init__(self, file_obj):
        self.file_obj = file_obj
        data = pickle.cargar(self.file_obj)
        self.players = data[0]
        self.historial_juego = data[1]

    def obtener_jugadores(self, func=None):
    
       '''return Jugador object
        recreated from a list
        func is callable which player
        may need for choice delegation'''
        
        res = []
        for colour, name, is_computer in self.players:
            if is_computer:
                player = Jugador(colour)
            else:
                player = Jugador(colour, name, func)
            res.append(player)
        return res

    def get_historial_juego(self):
        return self.historial_juego

    def __iter__(self):
        return iter(self.historial_juego)


class CreadorRegistro():
'''Guardar datos de la partida  
    como una lista anidada,  
    la cual se guarda con pickle'''


    def __init__(self):
        self.players = []
        self.historial_juego = []

    def add_player(self, player_obj):
       '''Acepta un objeto Jugador y  
    lo guarda NO como un objeto, sino como una lista'''

        if player_obj.choose_peón_delegate is None:
            is_computer = True
        else:
            is_computer = False
        self.players.append((player_obj.colour,
                             player_obj.name, is_computer))

    def add_game_turn(self, valor_dado, index):
        self.historial_juego.append((valor_dado, index))

    def guardar(self, file_obj):
        '''list of lists with players and
        game history
        '''
        pickle.dump([self.players, self.historial_juego],
                    file_obj)
#---------------------------------------

from os import linesep


class JuegoCLI():

    def __init__(self):
        self.prompt_end = "> "
        self.game = Game()
        # used for nicer print
        self.prompted_for_peón = False
        # saving game data
        self.record_maker = CreadorRegistro()
        # getting game data
        self.record_runner = None

    def validar_entrada(self, prompt, desire_type, allawed_input=None,
                       error_mess="Invalid Option!", str_len=None):
      '''
    Bucle que se repite hasta recibir un valor correcto  
    El parámetro allowed_input puede ser una lista de valores permitidos  
    El parámetro str_len es una tupla de dos valores (mínimo y máximo)
'''
        prompt += linesep + self.prompt_end
        while True:
            choice = input(prompt)
            if not choice:
                print(linesep + error_mess)
                continue
            try:
                choice = desire_type(choice)
            except ValueError:
                print(linesep + error_mess)
                continue
            if allawed_input:
                if choice in allawed_input:
                    break
                else:
                    print("Invalid Option!")
                    continue
            elif str_len:
                min_len, max_len = str_len
                if min_len < len(choice) < max_len:
                    break
                else:
                    print(linesep + error_mess)
            else:
                break
        print()
        return choice

    def get_user_initial_choice(self):
        text = linesep.join(["Escoja una opción",
                             "0 - iniciar nuevo juego"])
        choice = self.validar_entrada(text, int, (0))
        return choice


    def prompt_for_player(self):
      '''
    Obtiene los atributos del jugador desde la entrada,  
    inicializa una instancia de jugador y  
    agrega el jugador al juego.
'''

        available_colours = self.game.get_available_colours()
        text = linesep.join(["escoja tipo de jugador",
                             "0 - computador",
                             "1 - humano"])
        choice = self.validar_entrada(text, int, (0, 1))

        if choice == 1:
            name = self.validar_entrada("Ingrese un nombre para el jugador",
                                       str, str_len=(1, 30))
            available_options = range(len(available_colours))
            if len(available_options) > 1:
                # show available colours
                options = ["{} - {}".format(index, colour)
                           for index, colour in
                           zip(available_options,
                           available_colours)]
                text = "escoja un color" + linesep
                text += linesep.join(options)
                choice = self.validar_entrada(text, int, available_options)
                colour = available_colours.pop(choice)
            else:
                # only one colour left
                colour = available_colours.pop()
            player = Jugador(colour, name, self.prompt_choose_peón)
        elif choice == 0:
            # automatically assign colours
            colour = available_colours.pop()
            player = Jugador(colour)
        self.game.add_palyer(player)

    def solicitar_jugadores(self):
        '''put all players in the game'''
        counts = ("primer", "segundo", "tercer", "cuarto")
        text_add = "añadir {} jugador"
        for i in range(2):
            print(text_add.format(counts[i]))
            self.prompt_for_player()
            print("Jugador añadido")

        text = linesep.join(["escoja una opción:",
                             "0 - añadir jugador",
                             "1 - iniciar juego con  {} jugadores"])
        for i in range(2, 4):
            choice = self.validar_entrada(text.format(str(i)), int, (0, 1))
            if choice == 1:
                break
            elif choice == 0:
                print(text_add.format(counts[i]))
                self.prompt_for_player()
                print("Jugador añadido")

    def prompt_choose_peón(self):
        '''
    Se usa cuando un jugador (humano) tiene más de  
    un peón posible para mover.  
    Este método se pasa como un callable  
    durante la instanciación del jugador.
'''

        text = present_6_die_name(self.game.valor_dado,
                                  str(self.game.curr_player))
        text += linesep + "has more than one possible peóns to move."
        text += " Choose peón" + linesep
        peón_options = ["{} - {}".format(index + 1, peón.id)
                        for index, peón
                        in enumerate(self.game.peones_permitidos)]
        text += linesep.join(peón_options)
        index = self.validar_entrada(
            text, int, range(1, len(self.game.peones_permitidos) + 1))
        self.prompted_for_peón = True
        return index - 1

    def prompt_to_continue(self):
        text = "presone Enter para continuar" + linesep
        input(text)

    def print_players_info(self):
        word = "iniciar" if self.game.valor_dado is None else "continue"
        print("Game {} with {} players:".format(
              word,
              len(self.game.players)))
        for player in self.game.players:
            print(player)
        print()

    def print_info_after_turn(self):
        '''usa los atributos del juego para imprimir la info'''
        peóns_id = [peón.id for peón in self.game.peones_permitidos]
        # nicer print of dice
        message = present_6_die_name(self.game.valor_dado,
                                     str(self.game.curr_player))
        message += linesep
        if self.game.peones_permitidos:
            message_moved = "{} fue movido. ".format(
                self.game.picked_peón.id)
            if self.prompted_for_peón:
                self.prompted_for_peón = False
                print(message_moved)
                return
            message += "{} Es posible mover la ficha.".format(
                " ".join(peóns_id))
            message += " " + message_moved
            if self.game.jog_peóns:
                message += "Jog peón "
                message += " ".join([peón.id for peón in self.game.jog_peóns])
        else:
            message += "No es posible ese movimiento."
        print(message)

    def print_standing(self):
        standing_list = ["{} - {}".format(index + 1, player)
                         for index, player in enumerate(self.game.standing)]
        message = "Standing:" + linesep + linesep.join(standing_list)
        print(message)

    def print_board(self):
        print(self.game.get_board_pic())

    def run_recorded_game(self):
       '''
    Obtiene el historial de la partida  
    (valor del dado y el peón permitido por índice)  
    desde record_runner para volver a jugar la partida.
'''

        self.cargar_recorded_players()
        self.print_players_info()
        self.prompt_to_continue()
        for valor_dado, index in self.record_runner:
            self.game.jugar_turno(index, valor_dado)
            self.print_info_after_turn()
            self.print_board()
            self.prompt_to_continue()
            self.print_board()

    def continue_recorded_game(self):
        ''' Avanza el juego llamando al método jugar_turno  
    hasta el momento en que la partida fue interrumpida.'''

        self.cargar_recorded_players()
        self.record_players()
        for valor_dado, index in self.record_runner:
            self.game.jugar_turno(index, valor_dado)
            self.record_maker.add_game_turn(
                self.game.valor_dado, self.game.index)
        self.print_players_info()
        self.print_info_after_turn()
        self.print_board()

    def record_players(self):
        '''guardar players on recorder'''
        for player in self.game.players:
            self.record_maker.add_player(player)

    def cargar_recorded_players(self):
      '''  Obtiene los jugadores guardados  
    desde el registro y los agrega al juego.'''


        if self.record_runner is None:
            file_descr = self.prompt_for_file()
            self.record_runner = RegistroJuego(file_descr)
            file_descr.close()
        for player in self.record_runner.obtener_jugadores(
                self.prompt_choose_peón):
            self.game.add_palyer(player)

    def cargar_players_for_new_game(self):
        self.solicitar_jugadores()
        self.print_players_info()
        self.record_players()

    def play_game(self):
       '''  Principalmente llama al método jugar_turno  
    del juego mientras la partida no haya terminado.'''

        try:
            while not self.game.finished:
                self.game.jugar_turno()
                self.print_info_after_turn()
                self.print_board()
                self.record_maker.add_game_turn(
                    self.game.valor_dado, self.game.index)
                self.prompt_to_continue()
            print("Game finished")
            self.print_standing()
            self.offer_guardar_game()
        except (KeyboardInterrupt, EOFError):
            print(linesep +
                  "Exiting game. " +
                  "Save game and continue same game later?")
            self.offer_guardar_game()
            raise


    def iniciar(self):
        'metodo principal, iniciar cli'
        print()
        try:
            choice = self.get_user_initial_choice()
            if choice == 0:  # iniciar new game
                self.cargar_players_for_new_game()
                self.play_game()
            elif choice == 1:  # continue game
                self.continue_recorded_game()
                if self.game.finished:
                    print("Could not continue.",
                          "Game is already finished",
                          linesep + "Exit")
                else:
                    self.prompt_to_continue()
                    self.play_game()
            elif choice == 2:  # review played game
                self.run_recorded_game()
        except (KeyboardInterrupt, EOFError):
            print(linesep + "Exit Game")


if __name__ == '__main__':
    JuegoCLI().iniciar()

#_______________________




from collections import namedtuple, deque
import random


Pawn = namedtuple("Pawn", "index colour id")


class Jugador():

    "Conoce (almacena) sus peones,  
    también conoce su color  
    y elige qué peón mover  
    si hay más de uno posible."


    def __init__(self, colour, name=None, choose_peón_delegate=None):
  
  '''Si choose_peón_delegate no es None, se llama  
    con una lista de peones disponibles para mover  
    y se espera que devuelva el índice elegido'''
   ''' Si es None (lo que significa que es la computadora),  
    se elige un índice aleatorio'''


        self.colour = colour
        self.choose_peón_delegate = choose_peón_delegate
        self.name = name
        if self.name is None and self.choose_peón_delegate is None:
            self.name = "computer"
        self.finished = False
        # initialize four peóns with
        # id (first leter from colour and index (from 1 to 4))
        self.peóns = [Pawn(i, colour, colour[0].upper() + str(i))
                      for i in range(1, 5)]

    def __str__(self):
        return "{}({})".format(self.name, self.colour)

    def choose_peón(self, peóns):

  '''Delegar la elección al atributo de función  
    choose_peón_delegate si no es None.'''


        if len(peóns) == 1:
            index = 0
        elif len(peóns) > 1:
            if self.choose_peón_delegate is None:
                index = random.randint(0, len(peóns) - 1)
            else:
                index = self.choose_peón_delegate()
        return index


class Tablero():
   
   #Sabe dónde están los peones.  
    #Los peones están asignados a números de posición.  
    #Puede mover (cambiar el número de posición) un peón.  
   # Conoce otras cosas, como la distancia que un peón  
    #debe recorrer para llegar al final.Es solo el tablero. No conoce las reglas del juego 



    # common (sharojo) squares for all peóns
    BOARD_SIZE = 56

    # guardar (private) positions (squares) for each colour
    # This is squares just before peón finished
    BOARD_COLOUR_SIZE = 7

    COLOUR_ORDER = ['amarrillo', 'azul', 'rojo', 'verde']

    # distance between two neighbour colours
    # (The distance from iniciar square of one colour
    # to iniciar square of next colour)
    COLOUR_DISTANCE = 14

    def __init__(self):
        #fn1353c
        # get dict of iniciar position for every colour
        Tablero.COLOUR_START = {
            colour: 1 + index * Tablero.COLOUR_DISTANCE for
            index, colour in enumerate(Tablero.COLOUR_ORDER)}
        # get dict of end position for every colour
        Tablero.COLOUR_END = {
            colour: index * Tablero.COLOUR_DISTANCE
            for index, colour in enumerate(Tablero.COLOUR_ORDER)}
        Tablero.COLOUR_END['amarrillo'] = Tablero.BOARD_SIZE

        # dict where key is peón and
        # value is two size tuple holds position
        # Position is combination of
        # common (share) square and colourojo (private) square.
        self.peóns_possiotion = {}

        # painter is used to visually represent
        # the board and position of the peóns
        self.painter = PaintTablero()

        # pool means before iniciar1353
        self.board_pool_position = (0, 0)

    def set_peón(self, peón, position):
        '''guardar position'''
        self.peóns_possiotion[peón] = position

    def put_peón_on_board_pool(self, peón):
        self.set_peón(peón, self.board_pool_position)

    def is_peón_on_board_pool(self, peón):
        '''return True of False'''
        return self.peóns_possiotion[peón] == self.board_pool_position

    def put_peón_on_iniciaring_square(self, peón):
        iniciar = Tablero.COLOUR_START[peón.colour.lower()]
        position = (iniciar, 0)
        self.set_peón(peón, position)

    def can_peón_move(self, peón, valor_dado):
        '''check if peón can outside board colour size'''
        common_poss, private_poss = self.peóns_possiotion[peón]
        if private_poss + valor_dado > self.BOARD_COLOUR_SIZE:
            return False
        return True

    def move_peón(self, peón, valor_dado):
        '''change peón position, check
        if peón reach his color square
        '''
        common_poss, private_poss = self.peóns_possiotion[peón]
        end = self.COLOUR_END[peón.colour.lower()]
        if private_poss > 0:
            # peón is already reached own final squares
            private_poss += valor_dado
        elif common_poss <= end and common_poss + valor_dado > end:
            # peón is entering in own squares
            private_poss += valor_dado - (end - common_poss)
            common_poss = end
        else:
            # peón will be still in common square
            common_poss += valor_dado
            if common_poss > self.BOARD_SIZE:
                common_poss = common_poss - self.BOARD_SIZE
        position = common_poss, private_poss
        self.set_peón(peón, position)

    def does_peón_reach_end(self, peón):
      #si el peón se debe salir
        common_poss, private_poss = self.peóns_possiotion[peón]
        if private_poss == self.BOARD_COLOUR_SIZE:
            return True
        return False

    def get_peóns_on_same_postion(self, peón):
        '''return list of peóns on same position'''
        position = self.peóns_possiotion[peón]
        return [curr_peón for curr_peón, curr_postion in
                self.peóns_possiotion.items()
                if position == curr_postion]

    def paint_board(self):
        positions = {}
        for peón, position in self.peóns_possiotion.items():
            common, private = position
            if not private == Tablero.BOARD_COLOUR_SIZE:
                positions.setdefault(position, []).append(peón)
        return self.painter.paint(positions)


class Die():

    MIN = 1
    MAX = 6

    @staticmethod
    def throw():
        return random.randint(Die.MIN, Die.MAX)


class Game():
    #se conoce las reglas del juego

    def __init__(self):
        self.players = deque()
        self.standing = []
        self.board = Tablero()
        # is game finished
        self.finished = False
        # last rolled value from die (dice)
        self.valor_dado = None
        # player who last rolled die
        self.curr_player = None
        # curr_player's possible peón to move
        self.peones_permitidos = []
        # curr_player's chosen peón to move
        self.picked_peón = None
        # chosen index from allowed peón 
        self.index = None
        # jog peón if any 
        self.jog_peóns = []

    def add_palyer(self, player):
        self.players.append(player)
        for peón in player.peóns:
            self.board.put_peón_on_board_pool(peón)

    def get_available_colours(self):
        '''if has available colour on boards'''
        used = [player.colour for player in self.players]
        available = set(self.board.COLOUR_ORDER) - set(used)
        return sorted(available)

    def _get_next_turn(self):
     
    #Obtener el turno del siguiente jugador.  
    #Tiene un guion bajo porque, si se llama fuera de la clase, rompería el orden.


        if not self.valor_dado == Die.MAX:
            self.players.rotate(-1)
        return self.players[0]

    def get_peón_from_board_pool(self, player):
        '''when peón must iniciar'''
        for peón in player.peóns:
            if self.board.is_peón_on_board_pool(peón):
                return peón

    def get_peones_permitidos_to_move(self, player, valor_dado):
     
    #Devuelve todos los peones de un jugador  
    cuyo valor obtenido en el dado  
    les permite moverse.


        peones_permitidos = []
        if valor_dado == Die.MAX:
            peón = self.get_peón_from_board_pool(player)
            if peón:
                peones_permitidos.append(peón)
        for peón in player.peóns:
            if not self.board.is_peón_on_board_pool(peón) and\
                    self.board.can_peón_move(peón, valor_dado):
                peones_permitidos.append(peón)
        return sorted(peones_permitidos, key=lambda peón: peón.index)

    def get_board_pic(self):
        return self.board.paint_board()

    def _jog_foreign_peón(self, peón):
        peóns = self.board.get_peóns_on_same_postion(peón)
        for p in peóns:
            if p.colour != peón.colour:
                self.board.put_peón_on_board_pool(p)
                self.jog_peóns.append(p)

    def _make_move(self, player, peón):
   
    #Ordena al tablero que mueva un peón. Después del movimiento, pregunta al tablero  
    # si el peón llegó al final o si hizo retroceder a otros peones.  
   # Verifica si el peón y el jugador han terminado.


        if self.valor_dado == Die.MAX and\
                self.board.is_peón_on_board_pool(peón):
            self.board.put_peón_on_iniciaring_square(peón)
            self._jog_foreign_peón(peón)
            return
        self.board.move_peón(peón, self.valor_dado)
        if self.board.does_peón_reach_end(peón):
            player.peóns.remove(peón)
            if not player.peóns:
                self.standing.append(player)
                self.players.remove(player)
                if len(self.players) == 1:
                    self.standing.extend(self.players)
                    self.finished = True
        else:
            self._jog_foreign_peón(peón)

    def jugar_turno(self, ind=None, rolled_val=None):
 
   # Este es el método principal que se debe usar para jugar.  
   # El método solicita el turno del siguiente jugador,  
    lanza el dado, pide al jugador que elija un peón y lo mueve.  
      
   # "ind" y "rolled_val" son útiles cuando se necesita replicar (grabar) la partida.  
    # "ind" es el índice elegido de los peones permitidos.

        self.jog_peóns = []
        self.curr_player = self._get_next_turn()
        if rolled_val is None:
            self.valor_dado = Die.throw()
        else:
            self.valor_dado = rolled_val
        self.peones_permitidos = self.get_peones_permitidos_to_move(
            self.curr_player, self.valor_dado)
        if self.peones_permitidos:
            if ind is None:
                self.index = self.curr_player.choose_peón(
                    self.peones_permitidos)
            else:
                self.index = ind
            self.picked_peón = self.peones_permitidos[self.index]
            self._make_move(self.curr_player, self.picked_peón)
        else:
            self.index = -1
            self.picked_peón = None



#-------------------------------------------


from copy import deepcopy
from os import linesep


# board template (matrix)
BOARD_TMPL = [['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'A', 'M', 'A', 'R', 'I', 'L', 'L', 'O ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', 'V', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'A', 'Z', 'U', 'L', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', '-', '-', '>', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
            ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', '-', '-', '-', '-', '-', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '-', '-', '-', '-', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '-', '-', '-', '-', '#'],
            ['#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', 'X', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', '-', '-', '-', '-', '-', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '-', '-', '-', '-', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '-', '-', '-', '-', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#'],
            ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '<', '-', '-', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'V', 'E', 'R', 'D', 'E', '', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' #', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'R', 'O', 'J', 'O', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'],
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '^', ' ', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', '-', '-', '-', '-', '-', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '|', ' ', '#', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '|', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#'], 
            ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#']]

# Lista de tuplas de dos elementos.  
# El contenido de la tupla corresponde  
# con la dirección de la matriz BOARD_TMPL.  
# Mientras que el índice de la lista  
# corresponde con la posición compartida del peón  
# en la clase del tablero.

CODE_COMMON_SQUARES = [
    (),  # 0 index not used
    (14, 2), (14, 8), (14, 14), (14, 20), (14, 26), (14, 32), (14, 38),
    (12, 38), (10, 38), (8, 38), (6, 38), (4, 38), (2, 38), (2, 44),
    (2, 50), (4, 50), (6, 50), (8, 50), (10, 50), (12, 50), (14, 50),
    (14, 56), (14, 62), (14, 68), (14, 74), (14, 80), (14, 86), (16, 86),
    (18, 86), (18, 80), (18, 74), (18, 68), (18, 62), (18, 56), (18, 50),
    (20, 50), (22, 50), (24, 50), (26, 50), (28, 50), (30, 50), (30, 44),
    (30, 38), (28, 38), (26, 38), (24, 38), (22, 38), (20, 38), (18, 38),
    (18, 32), (18, 26), (18, 20), (18, 14), (18, 8), (18, 2), (16, 2)
]

# La tupla corresponde a la dirección de la matriz BOARD_TMPL.  
# El color corresponde al color del peón.  
# El índice de la lista de colores  
# corresponde con la posición privada (final) del peón.

CODE_COLOUR_SQUARES = {
    'amarrillo': [(), (16, 8), (16, 14), (16, 20), (16, 26), (16, 32), (16, 38)],
    'azul': [(), (4, 44), (6, 44), (8, 44), (10, 44), (12, 44), (14, 44)],
    'rojo': [(), (16, 80), (16, 74), (16, 68), (16, 62), (16, 56), (16, 50)],
    'verde': [(), (28, 44), (26, 44), (24, 44), (22, 44), (20, 44), (18, 44)]
}

# La tupla corresponde a la dirección de la matriz BOARD_TMPL.  
# El color corresponde al color del peón.  
# El índice de la lista de colores  
# corresponde con la posición inicial del peón.

CODE_POOL_PLACES = {
    'amarrillo': [(), (6, 14), (6, 19), (8, 14), (8, 19)],
    'azul': [(), (6, 71), (6, 76), (8, 71), (8, 76)],
    'rojo': [(), (24, 71), (24, 76), (26, 71), (26, 76)],
    'verde': [(), (24, 14), (24, 19), (26, 14), (26, 19)]
}


class PaintTablero():

    def __init__(self):
        self.board_tmpl_curr = deepcopy(BOARD_TMPL)

    def _place_peón(self, peón, position, offset):
        common_poss, private_poss = position
        colour = peón.colour.lower()
        if private_poss > 0:
            # private squares
            row, column = CODE_COLOUR_SQUARES[colour][private_poss]
        elif common_poss == 0:
            # pool 
            row, column = CODE_POOL_PLACES[colour][peón.index]
            offset = 0  # we do not need from offset in the pool only in squares 
        else:
            # common squares
            row, column = CODE_COMMON_SQUARES[common_poss]
        if offset > 0:
            self.board_tmpl_curr[row - 1][column + offset] = peón.id[1]
        else:
            self.board_tmpl_curr[row - 1][column - 1] = peón.id[0]
            self.board_tmpl_curr[row - 1][column] = peón.id[1]

    def _place_peóns(self, position_peóns):
        for position, peóns in position_peóns.items():
            for index, peón in enumerate(peóns):
                self._place_peón(peón, position, index)

    def paint(self, position):
   
   # Se espera un diccionario con:  
    - Clave: posiciones ocupadas.  
    - Valor: lista de peones en esa posición.


        self.board_tmpl_curr = deepcopy(BOARD_TMPL)
        self._place_peóns(position)
        board_paint = [''.join(row_list) for row_list in self.board_tmpl_curr]
        board_paint_str = linesep.join(board_paint)
        return board_paint_str


def present_6_die_name(number, name):

   # Impresión más clara del dado  
    #y el nombre del jugador.


    hor_line = 9 * '-'
    sps = 37 * ' '
    hor_line = sps + hor_line
    matrix = [['|       |', '|   #   |', '|       |'],
              ['|       |', '| #   # |', '|       |'],
              ['|     # |', '|   #   |', '| #     |'],
              ['| #   # |', '|       |', '| #   # |'],
              ['| #   # |', '|   #   |', '| #   # |'],
              ['| # # # |', '|       |', '| # # # |']]
    matrix = [[sps + cell for cell in row] for row in matrix]
    die = matrix[number - 1]
    die[1] = die[1] + "   " + name
    s = linesep.join([hor_line] + die + [hor_line])
    return s




