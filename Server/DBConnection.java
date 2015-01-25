import java.sql.*;

import model.Player;

public class DBConnection {

	private static final String USERNAME = "username";
	private static final String PASSWORD = "password";
	private static final String URL = "jdbc:mysql://localhost:3306/gameDB";
	
	private static Connection conn = null;
	private static Statement stmt = null;
	private static ResultSet rs = null;

	
	public static void openConnection() throws SQLException {

		conn = DriverManager.getConnection(URL, USERNAME, PASSWORD);

	}

	public static void closeResultSet() throws SQLException {

		if (rs != null) {
			rs.close();
		}
	}

	public static void closeStatementConnection() throws SQLException {

		if (stmt != null) {
			stmt.close();
		}
		if (conn != null) {
			conn.close();
		}
	}
	
	public static boolean isOpenConnection(){
		if(conn != null){
			return true;
		}
		return false;
	}
	
	public synchronized static void insertRow(Player player) throws SQLException {

		stmt = conn.createStatement();
		
		if(player != null){
			String query = "insert into player (username, password, position_x, position_y, position_z, heading, roll, pitch) values ('"
						+player.getUsername()+"', '"+player.getPassword()+"', "+player.getX()+", "+player.getY()+", "+player.getZ()
						+", "+player.getH()+", "+player.getR()+", "+player.getP()+");";

			stmt.executeUpdate(query);
		}else{
			System.err.println("Inser error: null data input.");
		}
	}
	
	public synchronized static boolean usernameExist(String username) throws SQLException{
		
		stmt = conn.createStatement();
		String query = "select username from player where username = '"+username+"';";
		
		rs = stmt.executeQuery(query);
		
		return rs.next();
	}
	
	public synchronized static String getPassword(String username) throws SQLException {
		
		stmt = conn.createStatement();
		
		String query = "select password from player where username = '"+username+"';";
		
		rs = stmt.executeQuery(query);
		
		if(rs.next()){
			 return rs.getString("password");
		}
		
		return null;
	}
	
	public synchronized static Player getPlayer(String username) throws SQLException {
		
		stmt = conn.createStatement();
		
		String query = "select * from player where username = '"+username+"';";
		
		rs = stmt.executeQuery(query);
		
		if(rs.next()){
			double x = rs.getDouble("position_x");
			double y = rs.getDouble("position_y");
			double z = rs.getDouble("position_z");
			double h = rs.getDouble("heading");
			double r = rs.getDouble("roll");
			double p = rs.getDouble("pitch");
			
			return new Player(username, x, y, z, h, r, p);
		}
		return null;
	}
	
	public synchronized static void updateRow(String username, double x, double y, double z, double h) throws SQLException{
		stmt = conn.createStatement();
		
		String query = "update player set position_x = "+x+", position_y = "+y+", position_z = "+z
				+", heading = "+h+" where username = '"+username+"';";
		
		stmt.executeUpdate(query);
	}
}
