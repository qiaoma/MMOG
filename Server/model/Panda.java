package model;

public class Panda {
	
	private String username;
	private double x;
	private double y;
	private double z;
	private double h;
	
	private String minDistancePlayer;
	private double minDistance;
	
	public Panda(String username){
		this.username = username;
		this.x = -107.575;
		this.y = 24.6066;
		this.z = -0.5;
		this.h = 60.5011;
		
		//initial mini-distance
		//this.minDistance = 20;
		//minDistancePlayer = "";
	}

	public String getUsername() {
		return username;
	}


	public void setUsername(String username) {
		this.username = username;
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

	public String getMinDistancePlayer() {
		return minDistancePlayer;
	}

	public void setMinDistancePlayer(String minDistancePlayer) {
		this.minDistancePlayer = minDistancePlayer;
	}

	public double getMinDistance() {
		return minDistance;
	}

	public void setMinDistance(double minDistance) {
		this.minDistance = minDistance;
	}
	
}
