from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from flask import Flask, render_template, request
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///findit.db"
db = SQLAlchemy(app)
lost_items = []
found_items=[]
class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    contact = db.Column(db.String(20))
    photo = db.Column(db.String(200))
    category=db.Column(db.String(50))

class FoundItem(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        item_name = db.Column(db.String(100))
        description = db.Column(db.String(200))
        contact = db.Column(db.String(20))
        photo = db.Column(db.String(200))
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    total_lost = LostItem.query.count()
    total_found = FoundItem.query.count()

    match_count = 0

    lost_items = LostItem.query.all()
    found_items = FoundItem.query.all()

    for lost in lost_items:
        for found in found_items:
            if lost.item_name.lower() == found.item_name.lower():
                match_count += 1

    return render_template(
        "home.html",
        total_lost=total_lost,
        total_found=total_found,
        match_count=match_count
    )

@app.route("/lost", methods=["GET", "POST"])
def lost():
    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        contact = request.form["contact"]
        category = request.form["category"]

        photo = request.files["photo"]

        if photo.filename != "":
            photo.save(os.path.join("static/uploads", photo.filename))

        new_item = LostItem(
        item_name=item_name,
        description=description,
        contact=contact,
        photo = photo.filename,
        category=category
    )

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("view_lost"))
    return render_template("lost.html")

@app.route("/found", methods=["GET", "POST"])
def found():
    if request.method == "POST":
        item_name = request.form["item_name"]
        description = request.form["description"]
        contact = request.form["contact"]
        photo = request.files["photo"]

        if photo.filename != "":
            photo.save(os.path.join("static/uploads", photo.filename))

        new_item = FoundItem(
            item_name=item_name,
            description=description,
            contact=contact,
            photo=photo.filename
        )  

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("view_found"))

    return render_template("found.html")
@app.route("/view_lost")
def view_lost():
    items = LostItem.query.all()
    return render_template(
        "view_lost.html",
        items=items
    )
@app.route("/view_found")
def view_found():
    items = FoundItem.query.all()

    return render_template(
        "view_found.html",
        items=items
    )


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        keyword = request.form["search"]

        lost_results = LostItem.query.filter(
            LostItem.item_name.contains(keyword)
        ).all()

        found_results = FoundItem.query.filter(
            FoundItem.item_name.contains(keyword)
        ).all()

        return render_template(
            "search_results.html",
            lost_results=lost_results,
            found_results=found_results
        )

    return render_template("search.html")

@app.route("/delete_lost/<int:item_id>")
def delete_lost(item_id):
    item = LostItem.query.get(item_id)

    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for("view_lost"))


@app.route("/matches")
def matches():

    lost_items = LostItem.query.all()
    found_items = FoundItem.query.all()

    matches = []

    for lost in lost_items:
        for found in found_items:

            if lost.item_name.lower() == found.item_name.lower():

                matches.append({
                    "lost": lost,
                    "found": found
                })

    return render_template(
        "matches.html",
        matches=matches
    )



@app.route("/edit_lost/<int:item_id>", methods=["GET", "POST"])
def edit_lost(item_id):

    item = LostItem.query.get(item_id)

    if request.method == "POST":

        item.item_name = request.form["item_name"]
        item.description = request.form["description"]
        item.contact = request.form["contact"]

        db.session.commit()

        return redirect(url_for("view_lost"))

    return render_template(
        "edit_lost.html",
        item=item
    )

@app.route("/delete_found/<int:item_id>")
def delete_found(item_id):

    item = FoundItem.query.get(item_id)

    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for("view_found"))


if __name__ == "__main__":
    app.run(debug=True)