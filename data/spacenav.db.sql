BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "BodyTypes" (
	"btype_id"	INTEGER NOT NULL UNIQUE,
	"btype_name"	TEXT NOT NULL,
	PRIMARY KEY("btype_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Cameras" (
	"cam_id"	INTEGER NOT NULL UNIQUE,
	"ortho"	TEXT NOT NULL DEFAULT 'False',
	"fov"	REAL NOT NULL DEFAULT 45.0,
	"znear"	REAL NOT NULL DEFAULT 0.1,
	"zfar"	NUMERIC NOT NULL DEFAULT 1.0,
	"pos"	TEXT NOT NULL DEFAULT 0.0,
	"aim"	TEXT NOT NULL DEFAULT 0.0,
	"up"	TEXT NOT NULL DEFAULT 0.0,
	"vel"	TEXT NOT NULL DEFAULT 0.0,
	"accel"	TEXT NOT NULL DEFAULT 0.0,
	"left"	REAL NOT NULL DEFAULT -1.0,
	"right"	REAL NOT NULL DEFAULT 1.0,
	"bottom"	REAL NOT NULL DEFAULT -1.0,
	"top"	REAL NOT NULL DEFAULT 1.0,
	PRIMARY KEY("cam_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Configs" (
	"cfg_id"	INTEGER NOT NULL UNIQUE,
	"cfg_path"	TEXT NOT NULL,
	"cfg_file"	TEXT NOT NULL,
	"cfg_desc"	TEXT NOT NULL,
	PRIMARY KEY("cfg_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "ConstTypes" (
	"const_id"	INTEGER NOT NULL UNIQUE,
	"const_type"	TEXT NOT NULL UNIQUE,
	"use_map"	TEXT NOT NULL,
	PRIMARY KEY("const_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "ConstValues" (
	"bod_id"	INTEGER NOT NULL,
	"const_id"	INTEGER NOT NULL,
	"abbrev"	TEXT NOT NULL DEFAULT '',
	"name"	TEXT NOT NULL DEFAULT '',
	"value"	REAL NOT NULL DEFAULT 0.0,
	"unit"	TEXT NOT NULL DEFAULT '',
	"uncertainty"	REAL NOT NULL DEFAULT 0.0,
	"reference"	TEXT NOT NULL DEFAULT '',
	"system"	TEXT NOT NULL DEFAULT 'si',
	PRIMARY KEY("bod_id","const_id"),
	FOREIGN KEY("bod_id") REFERENCES "SpaceBodies"("bod_id"),
	FOREIGN KEY("const_id") REFERENCES "ConstTypes"("const_id")
);
CREATE TABLE IF NOT EXISTS "DispSetups" (
	"dispset_id"	INTEGER NOT NULL UNIQUE,
	"rendBody"	TEXT NOT NULL DEFAULT 'wire',
	"showAxes"	INTEGER NOT NULL DEFAULT 1,
	"showStars"	INTEGER NOT NULL DEFAULT 1,
	"showRPY"	INTEGER NOT NULL DEFAULT 1,
	"showState"	INTEGER NOT NULL DEFAULT 1,
	"bodRadVec"	INTEGER NOT NULL DEFAULT 1,
	"showOsc"	INTEGER NOT NULL DEFAULT 1,
	"showTrail"	INTEGER NOT NULL DEFAULT 1,
	PRIMARY KEY("dispset_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Logs" (
	"log_id"	INTEGER NOT NULL UNIQUE,
	"timestamp"	REAL NOT NULL,
	"log_text"	TEXT NOT NULL,
	PRIMARY KEY("log_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "MenuItems" (
	"loc_key"	TEXT,
	"item_type"	TEXT,
	"label"	TEXT,
	"command"	TEXT,
	"menu"	TEXT,
	"tearoff"	INTEGER,
	"var"	TEXT,
	"value"	TEXT,
	"onvalue"	BLOB,
	"offvalue"	TEXT
);
CREATE TABLE IF NOT EXISTS "MiscSettings" (
	"miscset_id"	INTEGER NOT NULL UNIQUE,
	"epoch"	REAL NOT NULL DEFAULT 19700320.185600,
	"ephem_type"	TEXT NOT NULL DEFAULT 'jpl',
	"epoch_scale"	TEXT NOT NULL DEFAULT 'tdb',
	"format"	TEXT,
	"phys_model"	TEXT NOT NULL DEFAULT '2-body',
	"time_warp"	REAL NOT NULL DEFAULT 1.0,
	PRIMARY KEY("miscset_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Ships" (
	"ship_id"	INTEGER NOT NULL UNIQUE,
	"ship_name"	TEXT NOT NULL,
	PRIMARY KEY("ship_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "SpaceBodies" (
	"parent_id"	TEXT,
	"bod_id"	TEXT NOT NULL UNIQUE,
	"btype_id"	INTEGER NOT NULL DEFAULT 'star',
	"bod_name"	TEXT NOT NULL,
	"bod_symbol"	TEXT NOT NULL,
	"bod_clrRGBA"	TEXT NOT NULL,
	"bod_clrName"	TEXT NOT NULL,
	"bod_texFile"	TEXT NOT NULL,
	"bod_mass"	REAL,
	PRIMARY KEY("bod_id")
);
CREATE TABLE IF NOT EXISTS "TimeSpans" (
	"span_id"	INTEGER NOT NULL UNIQUE,
	"time_0"	REAL NOT NULL,
	"time_1"	REAL NOT NULL,
	"samples"	INTEGER NOT NULL,
	PRIMARY KEY("span_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "TkOptions" (
	"loc_key"	,
	"accelerator"	,
	"activebackground"	,
	"activeforeground"	,
	"background"	,
	"bitmap"	,
	"columnbreak"	,
	"compound"	,
	"font"	,
	"foreground"	,
	"hidemargin"	,
	"image"	,
	"offvalue"	,
	"onvalue"	,
	"selectcolor"	,
	"selectimage"	,
	"state"	,
	"underline"	,
	"value"	,
	"variable"	
);
CREATE TABLE IF NOT EXISTS "TrackFiles" (
	"trkFile_id"	INTEGER NOT NULL UNIQUE,
	"trkFilename"	TEXT NOT NULL,
	"trk_descr"	TEXT NOT NULL,
	PRIMARY KEY("trkFile_id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "TrackVals" (
	"trkValSet_id"	INTEGER NOT NULL UNIQUE,
	"trkVal_item1"	TEXT NOT NULL,
	PRIMARY KEY("trkValSet_id" AUTOINCREMENT)
);
INSERT INTO "BodyTypes" VALUES (0,'star');
INSERT INTO "BodyTypes" VALUES (1,'planet');
INSERT INTO "BodyTypes" VALUES (2,'moon');
INSERT INTO "BodyTypes" VALUES (3,'asteroid');
INSERT INTO "BodyTypes" VALUES (4,'comet');
INSERT INTO "BodyTypes" VALUES (5,'ship');
INSERT INTO "Cameras" VALUES (0,'False',45.0,0.1,1,'0.0,0.0,0.0','0.0,0.0,0.0','0.0,0.0,0.0','0.0,0.0,0.0','0.0,0.0,0.0',-1.0,1.0,-1.0,1.0);
INSERT INTO "Configs" VALUES (0,'..\data\','SNM_default.toml','basic default settings');
INSERT INTO "ConstTypes" VALUES (0,'k','0123456789a');
INSERT INTO "ConstTypes" VALUES (1,'R','0123456789a');
INSERT INTO "ConstTypes" VALUES (2,'R_mean','123456789a');
INSERT INTO "ConstTypes" VALUES (3,'R_polar','123456789a');
INSERT INTO "ConstTypes" VALUES (4,'J2','0234');
INSERT INTO "ConstTypes" VALUES (5,'J3','234');
INSERT INTO "ConstTypes" VALUES (6,'H0','3');
INSERT INTO "ConstTypes" VALUES (7,'rho0','3');
INSERT INTO "ConstTypes" VALUES (8,'Wdivc','0');
INSERT INTO "ConstValues" VALUES (0,0,'GM_sun','Heliocentric gravitational constant',1.32712442099e+20,'m3 / s2',10000000000.0,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (0,1,'R_sun','Sun equatorial radius',695700000.0,'m',0.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (0,4,'J2_sun','Sun J2 oblateness coefficient',2.2e-07,'',1.0e-09,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (0,8,'Wdivc_sun','total radiation power of Sun divided by the speed of light',102037593062041.0,'kg km / s2',1.0,'Howard Curtis','si');
INSERT INTO "ConstValues" VALUES (1,0,'GM_mercury','Mercury gravitational constant',22032090000000.0,'m3 / s2',0.91,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (1,1,'R_mercury','Mercury equatorial radius',2440530.0,'m',40.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (1,2,'R_mean_mercury','Mercury mean radius',2439400.0,'m',100.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (1,3,'R_polar_mercury','Mercury polar radius',2438260.0,'m',40.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (2,0,'GM_venus','Venus gravitational constant',324858592000000.0,'m3 / s2',0.006,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (2,1,'R_venus','Venus equatorial radius',6051800.0,'m',1000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (2,2,'R_mean_venus','Venus mean radius',6051800.0,'m',1000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (2,3,'R_polar_venus','Venus polar radius',6051800.0,'m',1000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (2,4,'J2_venus','Venus J2 oblateness coefficient',4.4044e-06,'',1.0,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (2,5,'J3_venus','Venus J3 asymmetry between the northern and southern hemispheres',-2.1082e-06,'',1.0,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (3,0,'GM_earth','Geocentric gravitational constant',398600441800000.0,'m3 / s2',800000.0,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (3,1,'R_earth','Earth equatorial radius',6378136.6,'m',0.1,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (3,2,'R_mean_earth','Earth mean radius',6371008.4,'m',0.1,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (3,3,'R_polar_earth','Earth polar radius',6356751.9,'m',0.1,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (3,4,'J2_earth','Earth J2 oblateness coefficient',0.00108263,'',1.0,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (3,5,'J3_earth','Earth J3 asymmetry between the northern and southern hemispheres',-2.5326613168e-06,'',1.0,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (3,6,'H0_earth','Earth H0 atmospheric scale height',8500.0,'m',1.0,'de Pater and Lissauer 2010','si');
INSERT INTO "ConstValues" VALUES (3,7,'rho0_earth','Earth rho0 atmospheric density prefactor',1.3,'kg / m3',1.0,'de Pater and Lissauer 2010','si');
INSERT INTO "ConstValues" VALUES (4,0,'GM_mars','Mars gravitational constant',42828374400000.0,'m3 / s2',0.00028,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (4,1,'R_mars','Mars equatorial radius',3396190.0,'m',100.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (4,2,'R_mean_mars','Mars mean radius',3389500.0,'m',2000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (4,3,'R_polar_mars','Mars polar radius',3376220.0,'m',100.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (4,4,'J2_mars','Mars J2 oblateness coefficient',0.0019555,'',1.0,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (4,5,'J3_mars','Mars J3 asymmetry between the northern and southern hemispheres',3.145e-05,'',1.0,'HAL archives','si');
INSERT INTO "ConstValues" VALUES (5,0,'GM_jupiter','Jovian system gravitational constant',1.2671276253e+17,'m3 / s2',2.0,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (5,1,'R_jupiter','Jupiter equatorial radius',71492000.0,'m',4000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2009','si');
INSERT INTO "ConstValues" VALUES (5,2,'R_mean_jupiter','Jupiter mean radius',69911000.0,'m',6000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2009','si');
INSERT INTO "ConstValues" VALUES (5,3,'R_polar_jupiter','Jupiter polar radius',6.6854,'m',10000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2009','si');
INSERT INTO "ConstValues" VALUES (6,0,'GM_saturn','Saturn gravitational constant',3.79312077e+16,'m3 / s2',1.1,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (6,1,'R_saturn','Saturn equatorial radius',60268000.0,'m',4000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (6,2,'R_mean_saturn','Saturn mean radius',58232000.0,'m',6000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (6,3,'R_polar_saturn','Saturn polar radius',54364000.0,'m',10000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (7,0,'GM_uranus','Uranus gravitational constant',5.7939393e+15,'m3 / s2',13.0,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (7,1,'R_uranus','Uranus equatorial radius',25559000.0,'m',4000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (7,2,'R_mean_uranus','Uranus mean radius',25362000.0,'m',7000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (7,3,'R_polar_uranus','Uranus polar radius',24973000.0,'m',20000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (8,0,'GM_neptune','Neptunian system gravitational constant',6.8365271005804e+15,'m3 / s2',10.0,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (8,1,'R_neptune','Neptune equatorial radius',24764000.0,'m',15000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (8,2,'R_mean_neptune','Neptune mean radius',24622000.0,'m',19000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (8,3,'R_polar_neptune','Neptune polar radius',24341000.0,'m',30000.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (9,0,'GM_pluto','Pluto gravitational constant',870300000000.0,'m3 / s2',3.7,'IAU 2009 system of astronomical constants','si');
INSERT INTO "ConstValues" VALUES (9,1,'R_pluto','Pluto equatorial radius',1188300.0,'m',1600.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (9,2,'R_mean_pluto','Pluto mean radius',1188000.0,'m',1600.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (9,3,'R_polar_pluto','Pluto polar radius',1188300.0,'m',1600.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (10,0,'GM_moon','Moon gravitational constant',4902799810000.0,'m3 / s2',7.74e-06,'Journal of Geophysical Research: Planets 118.8 (2013)','si');
INSERT INTO "ConstValues" VALUES (10,1,'R_moon','Moon equatorial radius',1737400.0,'m',0.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (10,2,'R_mean_moon','Moon mean radius',1737400.0,'m',0.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "ConstValues" VALUES (10,3,'R_polar_moon','Moon polar radius',1737400.0,'m',0.0,'IAU Working Group on Cartographic Coordinates and Rotational Elements: 2015','si');
INSERT INTO "DispSetups" VALUES (0,'wire',1,1,1,1,1,1,1);
INSERT INTO "MenuItems" VALUES ('0','mnu','main_menu',NULL,'root',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A','mnu','file_menu',NULL,'main_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A1','cmd','Load Default Setup','A1','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A2','sep','sepA2','NULL','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A3','cmd','Load Model','A3','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A4','cmd','Load Preferences','A4','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A5','cmd','Load Ships','A5','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A6','sep','sepA6','NULL','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A7','cmd','Save Model','A7','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A8','cmd','Save Preferenes','A8','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('A9','cmd','Save Ships','A9','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('AA','sep','sepAA','NULL','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('AB','cmd','Exit Space Nav','AB','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('AZ','cas','File','main_menu','file_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B','mnu','edit_menu',NULL,'main_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B1','cmd','Model Components','B1','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B2','cmd','Physics Models','B2','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B3','cmd','Epoch List','B3','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B4','sep','sepB4','NULL','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B5','cmd','Ship Registry','B5','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B6','cmd','Camera List','B6','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B7','cmd','Display Options','B7','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B8','sep','sepB8','NULL','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('B9','cmd','Logging Options','B9','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('BZ','cas','Edit','main_menu','edit_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C','mnu','view_menu',NULL,'main_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C1','cmd','Model Details','C1','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C2','chk','Show/Hide Viewer','C2','view_menu',0,'show_viewer',NULL,'True','False');
INSERT INTO "MenuItems" VALUES ('C3','sep','sepC3','NULL','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C4','cmd','Camera Status','C4','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C5','cmd','Viewer Scaling','C5','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C6','sep','sepC6','NULL','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C7','cmd','Ship Status','C7','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C8','cmd','Controls/Instruments','C8','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('C9','cmd','Condition Alarms','C9','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('CZ','cas','View','main_menu','view_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D','mnu','sim_menu',NULL,'main_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D1','cmd','Set Time Range','D1','sim_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D2','cmd','Set Sample Rate','D2','sim_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D3','cmd','Run Sim on Range','D3','sim_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D4','sep','sepD4','NULL','sim_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D5','cmd','Set Current Epoch','D5','sim_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D6','chk','Start/Stop Time','D6','sim_menu',0,'run_time',NULL,'True','False');
INSERT INTO "MenuItems" VALUES ('D7','mnu','warp_menu',NULL,'sim_menu',1,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D8','chk','Reverse Time Flow','D8','sim_menu',0,'fwd_time',NULL,'True','False');
INSERT INTO "MenuItems" VALUES ('D9','chk','Start/Stop Tracking','D9','sim_menu',0,'track_on',NULL,'True','False');
INSERT INTO "MenuItems" VALUES ('DZ','cas','Simulation','main_menu','sim_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E','mnu','data_menu',NULL,'main_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E1','cmd','Select Values to Track','E1','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E2','cmd','View Saved Tracks','E2','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E3','cmd','Run Track Stats','E3','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E4','cmd','Plot Tracks','E4','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E5','sep','sepE5','NULL','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('E6','cmd','View Log Files','E6','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('EZ','cas','Analysis','main_menu','data_menu',0,NULL,NULL,NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D71','cmd','x 0.1','D71','warp_menu',0,'time_warp','0.1',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D72','cmd','x 0.5','D72','warp_menu',0,'time_warp','0.5',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D73','cmd','x 0.9','D73','warp_menu',0,'time_warp','0.9',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D74','cmd','== 1.0','D74','warp_menu',0,'time_warp','1.0',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D75','cmd','x 1.1','D75','warp_menu',0,'time_warp','1.1',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D76','cmd','x 2.0','D76','warp_menu',0,'time_warp','2.0',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D77','cmd','x 10.0','D77','warp_menu',0,'time_warp','10.0',NULL,NULL);
INSERT INTO "MenuItems" VALUES ('D7Z','cas','Set Time Warp','sim_menu','warp_menu',1,NULL,NULL,NULL,NULL);
INSERT INTO "MiscSettings" VALUES (0,'1970-03-20T18:56:00.000','jpl','tdb','isot','2-body',1.0);
INSERT INTO "SpaceBodies" VALUES ('NULL','0','star','Sun','\u2609','255 255 0 255','yellow','8k_sun.jpg',1.98847544678817e+30);
INSERT INTO "SpaceBodies" VALUES ('0','1','planet','Mercury','\u263F','128 128 128 255','gray','8k_mercury.jpg',3.30114262939611e+23);
INSERT INTO "SpaceBodies" VALUES ('0','2','planet','Venus','\u2640','255 255 237 255','pale yellow','8k_venus_surface.jpg',4.86746625752164e+24);
INSERT INTO "SpaceBodies" VALUES ('0','3','planet','Earth','\u2641','0 255 0 255','green','2k_earth_daymap.jpg',5.97236535672332e+24);
INSERT INTO "SpaceBodies" VALUES ('0','4','planet','Mars','\u2642','183 65 14 255','rust','8k_mars.jpg',6.41712032220171e+23);
INSERT INTO "SpaceBodies" VALUES ('0','5','planet','Jupiter','\u2643','255 165 0 255','orange','8k_jupiter.jpg',1.89858021674898e+27);
INSERT INTO "SpaceBodies" VALUES ('0','6','planet','Saturn','\u2644','230 190 138 255','pale gold','8k_saturn.jpg',5.6833612572819e+26);
INSERT INTO "SpaceBodies" VALUES ('0','7','planet','Uranus','\u26E2','173 216 230 255','light blue','2k_uranus.jpg',8.68125539400187e+25);
INSERT INTO "SpaceBodies" VALUES ('0','8','planet','Neptune','\u2646','100 100 255 255','pale blue','2k_neptune.jpg',1.02433999900816e+26);
INSERT INTO "SpaceBodies" VALUES ('0','9','planet','Pluto','\u2647','255 20 147 255','pink','4k_makemake_fictional.jpg',1.30399995205332e+22);
INSERT INTO "SpaceBodies" VALUES ('3','10','moon','Moon','\u263E','192 192 192 255','light gray','8k_moon.jpg',7.34603092860739e+22);
COMMIT;
