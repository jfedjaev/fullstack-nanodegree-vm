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
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1>Hi, you can add restaurants here! Have fun!</h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/create'><p>What restaurant what you like to add?<p><input name="create" type="text" ><input type="submit" value="Submit"> </form>'''
                output += '<p><a titel="" href="/restaurants" >Go Back</a></p>'
                output += "</body></html>"
                self.wfile.write(output)
                print(output)
                return
            
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.displayRestaurants()                
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()      
                return


        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('create')


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
            print(output)
        except:
            pass
    
    def displayRestaurants(self):
        output = ""
        output += "<html><body>"
        output += "<h1>List of all Restaurants in the Area</h1>"
        output += "<em>Do you want to add new restaurants? Just click on the link below!</em>"
        output += '<p><a titel="" href="/restaurants/new" >Add a new restaurant</a></p>'
        output += "<hr />"
        output += "<hr />"
        
        restaurants = session.query(Restaurant).all()

        for restaurant in restaurants:
            output += "<li><b>{}</b>".format(restaurant.name) 
            output += '<p><a titel="" href="localhost:8080/edit" target="_blank">Edit</a></p>'
            output += '<p><a titel="" href="localhost:8080/delete" target="_blank">Delete</a></p>'
            output += "</li>"
            output += "<hr />"


        output += "</body></html>"
        self.wfile.write(output)
        print(output)
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