package model;


public class Player {
	
	private int playerId;
	private String username;
	private String password;
	private double x;
	private double y;
	private double z;
	private double h;
	private double r;
	private double p;
	
	public Player(){
	
	}
	//new player to register
	public Player(String username, String password){
		this.username = username;
		this.password = password;
		this.x = -107.575;
		this.y = 26.6066;
		this.z = -0.490075;
		this.h = 60.5011;
		this.r = 0;
		this.p = 0;
	}
	
	public Player(String username,
			double x, double y, double z, 
			double h){
		this.username = username;
		this.x = x;
		this.y = y;
		this.z = z;
		this.h = h;
		this.r = 0;
		this.p = 0;
	}
	
	public Player(String username,
			double x, double y, double z, 
			double h, double r, double p){
		this.username = username;
		this.x = x;
		this.y = y;
		this.z = z;
		this.h = h;
		this.r = r;
		this.p = p;
	}
	
	public int getPlayerId() {
		return playerId;
	}
	
	public void setPlayerId(int playerId) {
		this.playerId = playerId;
	}
	
	public String getUsername() {
		return username;
	}
	
	public void setUsername(String username) {
		this.username = username;
	}
	
	public String getPassword() {
		return password;
	}
	
	public void setPassword(String password) {
		this.password = password;
	}
	
	public double getX() {
		return x;
	}
	
	public void setX(double x) {
		this.x = x;
	}
	
	public double getY() {
		return y;
	}
	
	public void setY(double y) {
		this.y = y;
	}
	
	public double getZ() {
		return z;
	}
	
	public void setZ(double z) {
		this.z = z;
	}
	
	public double getH() {
		return h;
	}
	
	public void setH(double h) {
		this.h = h;
	}
	
	public double getR() {
		return r;
	}
	
	public void setR(double r) {
		this.r = r;
	}
	
	public double getP() {
		return p;
	}
	
	public void setP(double p) {
		this.p = p;
	}	
}

