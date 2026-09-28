"""Build the Maps query grid: 2 metros x 5 verticals x suburbs."""
import sys
KC = [("Kansas City","MO"),("Overland Park","KS"),("Olathe","KS"),("Lee's Summit","MO"),("Independence","MO"),
      ("Kansas City","KS"),("Lenexa","KS"),("Shawnee","KS"),("Blue Springs","MO"),("Liberty","MO")]
DFW = [("Dallas","TX"),("Fort Worth","TX"),("Plano","TX"),("Arlington","TX"),("Frisco","TX"),("McKinney","TX"),
       ("Irving","TX"),("Garland","TX"),("Denton","TX"),("Carrollton","TX"),("Grapevine","TX"),("Mesquite","TX"),
       ("Richardson","TX"),("Mansfield","TX")]
VERT = {"HVAC":"hvac contractor","Plumbing":"plumber","Electrical":"electrician","Roofing":"roofing contractor","GC":"general contractor"}
out = open(sys.argv[1] if len(sys.argv) > 1 else "queries.tsv", "w")
for metro, cities in (("KC", KC), ("DFW", DFW)):
    for v, term in VERT.items():
        for c, s in cities:
            out.write(f"{metro}\t{v}\t{c}\t{s}\t{term} {c} {s}\n")
