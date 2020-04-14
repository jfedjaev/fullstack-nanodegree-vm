# webserver imports
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi


# sql database imports
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

from database_setup import Base, Restaurant

# Create DB session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            ''' RENAME ''' 
            if self.path.endswith("/edit"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                rest_id = self.path.split('/')[1]

                print('The id of the restaurant is {}.'.format(rest_id))
                restaurant = session.query(Restaurant).filter_by(id = int(rest_id)).one()
                print(restaurant.name)

                output = ""
                output += "<html><body>"
                output += "<h1>You can edit the name of the restaurant << {} >> here.</h1>".format(restaurant.name)
                output += '''<form method='POST' enctype='multipart/form-data' action='/{}/edit'><p>What is the new name?<p><input name="name" type="text" ><input type="submit" value="Submit"> </form>'''.format(restaurant.id, restaurant.id)
                output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                output += "</body></html>"
                self.wfile.write(output)
                print('Posting rename...')
                return
            ''' END RENAME ''' 


            ''' START CREATE '''
            if self.path.endswith("/restaurants/create"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hi, you can add restaurants here!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/create'><p>What restaurant what you like to add?<p><input name="name" type="text" ><input type="submit" value="Submit"> </form>'''
                output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                output += "</body></html>"
                self.wfile.write(output)
                return
            ''' END CREATE '''

            ''' START DELETE '''
            if self.path.endswith("/delete"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                print('GET Delete..')
                rest_id = self.path.split('/')[1]

                #print('DELETE restaurant with id{}.'.format(rest_id))
                restaurant = session.query(Restaurant).filter_by(id = int(rest_id)).one()
                #print('DELETED {}.'.format(restaurant.name))

                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete <<< {} >>> ?</h1>".format(restaurant.name)
                output += '''<form method='POST' enctype='multipart/form-data' action='/{}/delete'><p>To confirm, please type click on "Delete"<p><input name="name" type="submit" ></form>'''.format(restaurant.id, restaurant.name)
                output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                output += "</body></html>"
                self.wfile.write(output)
                return
            ''' END DELETE '''
            
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.displayRestaurants()                
                return


        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:

            ''' CREATE NEW RESTAURANT '''
            if self.path.endswith('/create'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('name')


                    try:
                        rest_name = messagecontent[0]
                        print('Adding {} to the database...').format(rest_name)
                        new_restaurant = Restaurant(name = rest_name)
                        session.add(new_restaurant)
                        session.commit()
                        print('Restaurant {} successfully added!'.format(new_restaurant))
                    except SQLAlchemyError as e:
                        print(e)

                    output = ""
                    output += "<html><body>"
                    output += " <h1>Congratulations!</h1>"
                    output += "<p>You just added <em>{}</em> to the database. <p>".format(messagecontent[0])
                    output += "<h3>Do you want to add another one?</h3>"
                    output += '''<form method='POST' enctype='multipart/form-data' action='/create'><p>What restaurant what you like to add?<p><input name="create" type="text" ><input type="submit" value="Submit"> </form>'''
                    output += "<hr />"
                    output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                    output += "</body></html>"
                    self.wfile.write(output)
            ''' END CREATE NEW RESTAURANT '''



            ''' EDIT/RENAME RESTAURANT '''
            if self.path.endswith('edit'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                print('POST Rename in progress...')
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('name')

                    rest_id = self.path.split('/')[1]

                    print('The id of RENAME restaurant is {}.'.format(rest_id))
                    restaurant = session.query(Restaurant).filter_by(id = int(rest_id)).one()
                    print('Message content is: {}'.format(messagecontent))
                    restaurant.name = messagecontent[0]
                    session.add(restaurant)
                    session.commit()
                    print('New restaurant name is: {}'.format(messagecontent[0]))
                    print('Name successfully changed to {}.'.format(restaurant.name))

                    output = ""
                    output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                    self.wfile.write(output)

            ''' END RENAME '''

            ''' START DELETE '''
            if self.path.endswith('/delete'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                print('POST Deletion in progress...')
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('name')

                    rest_id = self.path.split('/')[1]

                    print('The id of DELETE restaurant is {}.'.format(rest_id))
                    restaurant = session.query(Restaurant).filter_by(id = int(rest_id)).one()
                    print('Message content is: {}'.format(messagecontent[0]))
                    session.delete(restaurant)
                    session.commit()
                    print('DELETE restaurant name is: {}'.format(messagecontent[0]))
                    print('Name successfully DELETED: {}.'.format(restaurant.name))

                    output = "<h1>Successfull!"
                    output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                    self.wfile.write(output)

            ''' END DELETE '''


        except:
            pass
    
    def displayRestaurants(self):
        output = ""
        output += "<html><body>"
        output += "<h1>List of all Restaurants in the Area</h1>"
        output += "<em>Do you want to add new restaurants? Just click on the link below!</em>"
        output += '<p><a titel="" href="/restaurants/create" >Add a new restaurant</a></p>'
        output += "<hr />"
        output += "<hr />"
        
        restaurants = session.query(Restaurant).all()

        for restaurant in restaurants:
            output += "<li><b>{}</b>".format(restaurant.name) 
            output += '<p><a titel="" href="/{}/edit" >Edit</a></p>'.format(restaurant.id)
            output += '<p><a titel="" href="/{}/delete" >Delete</a></p>'.format(restaurant.id)
            output += "</li>"
            output += "<hr />"


        output += "</body></html>"
        self.wfile.write(output)
        return


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web Server running on port {}".format(port) 
        server.serve_forever()


    except KeyboardInterrupt:
        print("^C entered, stopping web server....")
        server.socket.close()

if __name__ == '__main__':
    main()