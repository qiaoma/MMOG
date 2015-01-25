import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.ByteArrayOutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import model.Panda;
import model.Player;

/**
 * A server program which accepts requests from clients to
 * capitalize strings.  When clients connect, a new thread is
 * started to handle an interactive dialog in which the client
 * sends in a string and the server thread sends back the
 * capitalized version of the string.
 *
 * The program is runs in an infinite loop, so shutdown in platform
 * dependent.  If you ran it from a console window with the "java"
 * interpreter, Ctrl+C generally will shut it down.
 */
public class CapitalizeServer {

    /**
     * The server runs in an infinite loop listening on port 9898.
     * When a connection is requested,
     * it spawns a new thread to do the servicing and immediately returns to listening.
     * The server keeps a unique client number for each
     * client that connects just to show interesting logging
     * messages.  It is certainly not necessary to do this.
     */
	
	private static final String LOGIN = "1";
	private static final String REGISTER = "2";
	private static final String UPDATE_PLAYER_MOVE = "4";
	private static final String PANDA_ATTACK_REQUEST = "5";
	
	private static final String USERNAME_EXIST = "111";
	private static final String REGISTER_SUCCESSFUL = "110";
	private static final String LOGIN_SUCCESSFUL = "100";
	private static final String LOGIN_FAIL = "101";
	private static final String ADD_NEW_PLAYER = "102";
	
	private static final String LOGOUT = "120";
	
	private static final String UPDATE_PLAYER_MOVE_RESPONSE = "130";
	
	private static final String PANDA_ATTACK = "140";
	
	private static final int PANDA_ATTACK_RANGE = 10;
	
	//private static HashMap<Integer, Capitalizer> activeThreads;
	private static ArrayList<Capitalizer> activeThreads;
	private static HashMap<String, Player> activePlayers;
	private static HashMap<String, Double> possibleTargets;
	private static Panda panda;

    public static void main(String[] args) throws Exception {
    	
    	//activeThreads = new HashMap<>();
    	activeThreads = new ArrayList<>();
    	activePlayers = new HashMap<>();
    	possibleTargets = new HashMap<>();
 
    	panda = new Panda("panda");
    	
        System.out.println("The capitalization server is running.");
        int clientNumber = 0;
        ServerSocket listener = new ServerSocket(9898);
        try {
            while (true) {
            	Capitalizer capitalizer = new Capitalizer(listener.accept(), clientNumber++);
            	//activeThreads.put(clientNumber, capitalizer);
            	activeThreads.add(capitalizer);
            	capitalizer.start();   
                //new Capitalizer(listener.accept(), clientNumber++).start();
            }
        } finally {
            listener.close();
        }
    }

    private static class Capitalizer extends Thread {
        private Socket socket;
        private int clientNumber;
        Player player;
        
        DataInputStream din;
        OutputStream out;

        public Capitalizer(Socket socket, int clientNumber) {
            this.socket = socket;
            this.clientNumber = clientNumber;
            log("New connection with client# " + clientNumber + " at " + socket);
        }

        /**
         * Services this thread's client by first sending the
         * client a welcome message then repeatedly reading strings
         * and sending back the capitalized version of the string.
         */
        public void run() {
        	String taskCode = "";
            try {

				// Streams

                InputStream in = socket.getInputStream();
                din = new DataInputStream(in);
                out = socket.getOutputStream();
        		DataOutputStream dout = new DataOutputStream(out);
        		
        		DBConnection.openConnection();
				// read a request from a client,
				// capitalize,
				// and then send a response to the client

				while (true) {

					String input = getInput();
                    //System.out.println("Input is : " + input);                  
                    String[] inputs = input.split(" ");                      	
                	taskCode = inputs[0];           
                    
                	if(taskCode.equals(LOGIN)){
               		 	//login
	               		String username = inputs[1];
	               		String password = inputs[2];                          		                    			               		
	               		loginResponse(username, password);	               		
	               		
                	}else if(taskCode.equals(REGISTER)){
                		//register
                		String username = inputs[1];
                		String password = inputs[2];                   		                    		 
                		registerResponse(username, password);                  		
                	}else if(taskCode.equals(LOGOUT)){                		
                		//logout               		              		
            			logoutResponse(inputs[1]);
                             		
                	}else if(taskCode.equals(UPDATE_PLAYER_MOVE)){
                		
                		updatePlayerMoveResponse(inputs[1]);
                	}else if(taskCode.equals(PANDA_ATTACK_REQUEST)){
                		//inputs[1] contains username               		
                		pandaAttackResponse(inputs[1]);
                	}
                }
            } catch (IOException e) {
            	
            	//Save to database when user close socket       		       		
                //log("Error handling client# " + clientNumber + ": " + e);
            } catch (SQLException e1) {
				System.out.println(e1);
			}catch(Exception e1){
				
				System.out.println(e1);
			}finally {
                try {
                	if(!DBConnection.isOpenConnection()){
                		DBConnection.openConnection();
                	}					
                	//DBConnection.closeResultSet();
                	//DBConnection.closeStatementConnection();  
                    socket.close();
                    log("Save client's latest data to database in final block");
                } catch (IOException e) {
                	log("Connection with client# " + clientNumber + " closed");
                }catch (SQLException e1) {
    				System.out.println(e1);
    			}               
            }
        }
        
        public void loginResponse(String username, String password) throws SQLException, IOException{
        	if( password.equals(DBConnection.getPassword(username)) ){
       			player = DBConnection.getPlayer(username);
       			setActivePlayer(username, player);
       			
       			//broadcast all players new player added
       			//send the new player a list of current players
       			//send all other players the new player position
       				               			
       			String playerOutput = ADD_NEW_PLAYER+" "+username+","+player.getX()+","+player.getY()
       					+","+player.getZ()+","+player.getH();
       			
       			String playerListOutput = LOGIN_SUCCESSFUL+" ";
       			      			
       			for(Player p : activePlayers.values()){
       				playerListOutput += p.getUsername()+","+p.getX()+","+p.getY()
       						+","+p.getZ()+","+p.getH()+":";
       				
       			}
       			playerListOutput += panda.getUsername()+","+panda.getX()+","+panda.getY()
   						+","+panda.getZ()+","+panda.getH();

       			byte[] playerBytesOutput = getOutput(playerOutput);	               			
       			byte[] playerListBytesOutput = getOutput(playerListOutput);
       			
       			for(Capitalizer cap :  activeThreads){	               				
       				if(cap.player.getUsername().equals(username)){
       					//send the new player a list of current players
       					cap.out.write(playerListBytesOutput);
       				}else{
       					//send all other players the new player position
       					cap.out.write(playerBytesOutput);
       				}	               				
        		}	               					      			
    			log("Client "+username+" login");
       		}else{
       			sendOutput(LOGIN_FAIL+" LoginFail");
    			log("Client login fail");
       		}
        }
        
        public void logoutResponse(String msg) throws Exception{
    		String[] msgs = msg.split(",");
    		String username = msgs[0];
			double x = Double.parseDouble(msgs[1]);
			double y = Double.parseDouble(msgs[2]);
			double z = Double.parseDouble(msgs[3]);
			double h = Double.parseDouble(msgs[4]);
    		
			if(!DBConnection.isOpenConnection()){
        		DBConnection.openConnection();
        	}
    		DBConnection.updateRow(username, x, y, z, h);

    		removeActiveThreads(username);            			
			String logoutMsg = LOGOUT+" "+username;
			sendMsgToActiveThreads(logoutMsg);
			removeActivePlayer(username);
			
			log(username+" logout");
        }
        
        public void updatePlayerMoveResponse(String msg) throws Exception{
    		//msg contains username,x,y,z,h             		
    		
    		//send to all active threads. client responses to check if update move need
    		String sendMsg = UPDATE_PLAYER_MOVE_RESPONSE+" "+msg;               		  		
    		sendMsgToActiveThreads(sendMsg);  
        }
        
        public void pandaAttackResponse(String msg) throws Exception{
        	//msg contains username and distance
        	
        	String[] msgs = msg.split(",");
        	String username = msgs[0];
        	double distance = Double.parseDouble(msgs[1]);
        	
        	//update distance hash-map
        	if(possibleTargets.containsKey(username)){
        		possibleTargets.remove(username);       		
        	}
        	possibleTargets.put(username, distance);
        	
        	String targetUsername = getTargetUsername(username, distance);
        	
        	log("distance: "+distance);
        	log("target "+targetUsername);
        	
        	sendMsgToActiveThreads(PANDA_ATTACK+" "+targetUsername);
        }
        
        public String getTargetUsername(String user, double distance){
        	
        	String targetUsername = user;
        	double miniDistance = distance;
        	for(Map.Entry<String, Double> en : possibleTargets.entrySet()){
        		if(miniDistance > en.getValue()){
        			miniDistance = en.getValue();
        			targetUsername = en.getKey();
        		}
        	}
        	
        	//Player targetPlayer = activePlayers.get(targetUsername);
        	return targetUsername;
        }
        
        public void removeActiveThreads(String username){
        	for(Capitalizer cap :  activeThreads){	               				          				
   				if(cap.player.getUsername().equals(username)){
   					activeThreads.remove(cap);
   					break;
   				}
    		}
        }
        
        public void sendMsgToActiveThreads(String msg) throws Exception{
        	byte[] bytesOutput = getOutput(msg);	
			for(Capitalizer cap :  activeThreads){								
				if(cap.out != null){					
					cap.out.write(bytesOutput);
				}
    		}
        }
        
        public String getInput() throws IOException{
        	short stringLength = Short.reverseBytes(din.readShort());
		    //System.out.println(stringLength);
		    byte[] buffer = new byte[stringLength-2];
		    din.skipBytes(2);
			din.read(buffer, 0, stringLength-2);
			String input = new String(buffer);
			return input;
        }
        
        public byte[] getOutput(String output){
        	// generate an output
            ByteArrayOutputStream tmp = new ByteArrayOutputStream();

            // initialize two bytes for the packet size
            tmp.write(0xff);
			tmp.write(0xff);

			// write a string
			tmp.write(conv((short) output.length()), 0, 2);
			tmp.write(output.getBytes(), 0, output.length());

			byte[] bytes = tmp.toByteArray();
			// Update the length of packet size without counting these two bytes.
			bytes[0] = (byte) ((tmp.size() - 2 ) & 0xff);
			bytes[1] = (byte) ((tmp.size() - 2 ) >> 8);
			
			return bytes;
        }
        
        public void sendOutput(String output) throws IOException{

        	byte[] bytes = getOutput(output);
			out.write(bytes);
        }
        
        public void registerResponse(String username, String password) throws SQLException, IOException{
        	//store in DB		
			if(DBConnection.usernameExist(username)){
				sendOutput(USERNAME_EXIST + " UsernameExist");
				log("Username exist.");
			}else{
				Player player = new Player(username, password);
				DBConnection.insertRow(player);
				sendOutput(REGISTER_SUCCESSFUL + " Registered");
				log("New Player " + username + " is registered!");
			}				 
        }
        
        public void setActivePlayer(String username, Player player) {
            activePlayers.put(username, player);
        }
        
        public void removeActivePlayer(String username) {
            activePlayers.remove(username);
        }
        
        /**
         * Logs a simple message.  In this case we just write the
         * message to the server applications standard output.
         */
        private void log(String message) {
            System.out.println(message);
        }


		public byte[] conv(short short_val) {
		     byte[] b = new byte[2];

		            b[0] = (byte) (short_val);      // Lo
		            b[1] = (byte) (short_val >> 8); // Hi

			 return b;

		}

    }
}