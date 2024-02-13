from models import *
import os
from sqlalchemy.exc import IntegrityError
from functools import wraps
from assets import *


@app.before_request
def before_request():
    flask_session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=20)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' in flask_session:
            if get_user_by_username(flask_session["user"]['username']):
                return f(*args, **kwargs)
            else:
                return redirect(url_for("login"))
        else:
            flash('Login required.', "danger")
            return redirect(url_for("login"))

    return wrap


def redirect_if_get(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.method == "POST":
            return f(*args, **kwargs)
        else:
            return redirect(url_for("home"))

    return wrap


def create_user(username, firstname, lastname, is_admin=False):
    try:
        created_user = User(username, firstname, lastname, is_admin)
        db.session.add(created_user)
        db.session.commit()
        return created_user
    except IntegrityError as e:
        print(e)


def get_user_by_username(username, get_pass=False):
    try:
        user = User.query.filter_by(username=f"{username.strip()}").first().__dict__
        user.pop("_sa_instance_state")
        if not get_pass:
            user.pop("password")
        return user
    except:
        return


def get_user_by_id(id):
    try:
        user = User.query.filter_by(id=id).first().__dict__
        user.pop("_sa_instance_state")
        user.pop("password")
        return user
    except:
        return


def check_login(username, user_password):
    user = get_user_by_username(username)
    if user:
        return bcrypt.check_password_hash(user.password, user_password)


# create_user("keerajk", "Keerthana", "K", False)


# create_user("dhivakac", "Dhivakar", "Chelladurai")

def get_users():
    data_list = [user_data.__dict__ for user_data in User.query.all()]
    for item in data_list:
        item.pop("_sa_instance_state")
        item.pop("password")
    return data_list


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), "media/amazon_blink.gif", mimetype='image/gif')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login = dict(request.form)
        if 'user' not in flask_session:
            user_data = get_user_by_username(login["username"], True)
            if user_data:
                if bcrypt.check_password_hash(user_data["password"], login["password"]):
                    user_data.pop('password')
                    flask_session['user'] = user_data
                    return redirect(url_for('home'))
                flash("Login credentials for <kbd id='last_user' data-user='" + login["username"] + "'>" + login[
                    "username"] + "</kbd> doesn't match. Try again.", "warning")
                return redirect(url_for("login"))
            flash("User <kbd>" + login["username"] + "</kbd> isn't registered. <br> Contact your team leads.", "danger")
            return redirect(url_for("login"))
    if 'user' in flask_session:
        return redirect(url_for('home'))
    return render_template('login.html', greeting=False)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')
        firstname = request.form.get('first_name')
        lastname = request.form.get('last_name')

        # Create a new user instance
        new_user = User(username=username, password=password, firstname=firstname, lastname=lastname, is_admin=False)
        db.session.add(new_user)
        db.session.commit()
    return render_template('signup.html')


@app.route('/qa_data')
def qa_data():
    return render_template('qa_data.html')


@app.route('/')
@login_required
def home():
    current_date = datetime.datetime.now().strftime("%m-%d-%Y")
    print(current_date)
    if flask_session["user"]['is_admin']:
        try:
            daily_prod = get_daily(current_date, None)
            prod_data_flat = [data[0] for data in daily_prod]
        except:
            prod_data_flat = []
        return render_template('index.html', prod_data=prod_data_flat)
    else:
        daily_prod = calc_prod(current_date, None, flask_session["user"]['username'])
        return render_template('index.html', prod_data=daily_prod)


@app.route("/daily/<date>", methods=["GET", "POST"])
@login_required
@redirect_if_get
def daily_json(date):
    if request.method == "POST":
        try:
            daily_prod = get_daily(datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d-%Y"), None)
            prod_data_flat = [data[0] for data in daily_prod]

            if not flask_session["user"]['is_admin']:
                temp_list = []
                for data in prod_data_flat:
                    if data["username"] == flask_session["user"]["username"]:
                        temp_list.append(data)
                prod_data_flat = temp_list
        except:
            prod_data_flat = []
        return {
            "data": prod_data_flat
        }


@app.route("/date_range/<start_date>/<end_date>", methods=["GET", "POST"])
@login_required
@redirect_if_get
def date_range_json(start_date, end_date):
    if request.method == "POST":
        try:
            date_range_prod = get_range_prod(datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%m-%d-%Y"),
                                             datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%m-%d-%Y"))
            prod_data_flat = []
            for user in date_range_prod.keys():
                prod_data_flat.append({
                    "username": user,
                    "prod_mins": date_range_prod[user]["total_calc"]["prod_mins"],
                    "non_prod_mins": date_range_prod[user]["total_calc"]["non_prod_mins"],
                    "util_mins": date_range_prod[user]["total_calc"]["util_mins"],
                    "daily_util": date_range_prod[user]["total_calc"]["daily_util"],
                    "daily_prod": date_range_prod[user]["total_calc"]["daily_prod"]
                })

            if not flask_session["user"]['is_admin']:
                temp_list = []
                for data in prod_data_flat:
                    if data["username"] == flask_session["user"]["username"]:
                        temp_list.append(data)
                prod_data_flat = temp_list
        except Exception as e:
            print(e)
            prod_data_flat = []
        return {
            "data": prod_data_flat
        }


@app.route("/qa_data/date_range/<start_date>/<end_date>", methods=["GET", "POST"])
@login_required
@redirect_if_get
def qa_date_range_json(start_date, end_date):
    if request.method == "POST":
        try:
            date_range_prod = get_range_merch(datetime.datetime.strptime(start_date, "%Y-%m-%d").strftime("%m-%d-%Y"), datetime.datetime.strptime(end_date, "%Y-%m-%d").strftime("%m-%d-%Y"))
        except Exception as e:
            date_range_prod = []
        html = ""
        for data in date_range_prod:

            html += f"""
                <tr>
                    <td>Merchandising</td>
                    <td>{ data }</td>
                    <td><input name="poc" type="text" class="form-control" required></td>
                    <td>{ date_range_prod[data]["email"] }</td>
                    <td>{ date_range_prod[data]["onsite"] }</td>
                    <td>{ date_range_prod[data]["push"] }</td>
                    <td>{ date_range_prod[data]["vendisto"] }</td>
                    <td>{ date_range_prod[data]["validation"] }</td>
                    <td>{ sum([date_range_prod[data]["email"], date_range_prod[data]["onsite"], date_range_prod[data]["push"], date_range_prod[data]["vendisto"], date_range_prod[data]["validation"] ]) }</td>
                </tr>
            """

        return {
            "data": html
        }


@app.route('/assets/marketplace')
@login_required
def get_marketplaces():
    return {
        "data": [marketplace.as_dict() for marketplace in Marketplace.query.all()]
    }


@app.route('/assets/process/<id>')
@login_required
def get_processes(id):
    return {
        "data": [process.as_dict() for process in Process.query.filter_by(marketplace_id=id)]
    }


@app.route('/assets/deal/<id>')
@login_required
def get_deals(id):
    return {
        "data": [deal.as_dict() for deal in Deal.query.filter_by(process_id=id)]
    }


def get_tree():
    with app.app_context():
        marketplaces = Marketplace.query.all()
        processes = Process.query.all()
        deals = Deal.query.all()

    marketplace_id_to_tree_id = {}
    process_id_to_tree_id = {}
    deal_to_tree_id = {}

    overall_id = 0

    for marketplace in marketplaces:
        overall_id += 1
        marketplace_id_to_tree_id[marketplace.id] = overall_id

    for process in processes:
        overall_id += 1
        process_id_to_tree_id[process.id] = overall_id

    for deal in deals:
        overall_id += 1
        deal_to_tree_id[deal.id] = overall_id

    data = []

    for marketplace in marketplaces:
        data.append(f"""{{
    n_value: 'marketplace_{marketplace.id}',
    n_title: '{marketplace.name} (Marketplace)',
    n_id: {marketplace_id_to_tree_id[marketplace.id]},
    n_parentid: 0,
    n_checkStatus: false,
    n_elements: [
        {{
            icon: 'fa fa-edit',
            title: 'Add Process',
            onClick: (node) => {{
                swal_bootstrap.fire({{
                    title: 'Add Process',
                    html: `
                    <div class="text-center">
                        <label for="process">Name</label>
                        <input type="text" id="process" class="swal2-input">
                    </div>
                    `,
                    confirmButtonText: 'Save',
                    focusConfirm: false,
                    preConfirm: () => {{
                        var process_name = Swal.getPopup().querySelector('#process').value
                        if (!process_name) {{
                            swal_bootstrap.showValidationMessage(`Process name cannot be empty.`)
                        }}
                        return {{ process_name: process_name, marketplace: "{marketplace.id}" }}
                    }}
                }}).then((result) => {{
                    $.ajax({{
                        type: "POST",
                        contentType: "application/json",
                        url: '/process/add',
                        data: JSON.stringify(result["value"]),
                        success: function(response) {{ 
                            if(response["operation"]){{ 
                                swal_bootstrap.fire({{
                                    icon: 'success',
                                    title: 'Add Process',
                                    text: 'Created ' + response["data"]["name"] + ' (Process) under ' + node.title + "."
                                }})
                                .then(() => {{
                                    window.location.href = window.location.href
                                }})
                            }}
                        }},
                        dataType: 'json'
                    }});
                }})
            }}
        }}]
}}""")

    for process in processes:
        data.append(f"""{{
    n_value: 'process_{process.id}',
    n_title: '{process.name} (Process)',
    n_id: {process_id_to_tree_id[process.id]},
    n_parentid: {marketplace_id_to_tree_id[process.marketplace_id]},
    n_checkStatus: false,
    n_elements: [
        {{
            icon: 'fa fa-edit',
            title: 'Add Deal',
            onClick: (node) => {{
                swal_bootstrap.fire({{
                    title: 'Add Deal',
                    html: `
                    <div class="text-center">
                        <label for="deal">Name</label>
                        <input type="text" id="deal" class="swal2-input">
                        
                        <label for="build_aht">Build AHT</label>
                        <input type="number" minimum=1 id="build_aht" class="swal2-input">

                        <label for="audit_aht">Audit AHT</label>
                        <input type="number" minimum=1 id="audit_aht" class="swal2-input">
                    </div>
                    `,
                    confirmButtonText: 'Save',
                    focusConfirm: false,
                    preConfirm: () => {{
                        var deal_name = Swal.getPopup().querySelector('#deal').value
                        var build_aht = Swal.getPopup().querySelector('#build_aht').value
                        var audit_aht = Swal.getPopup().querySelector('#audit_aht').value
                        if (!deal_name) {{
                            swal_bootstrap.showValidationMessage(`Deal name cannot be empty.`)
                        }}

                        if (!build_aht || !audit_aht) {{
                            swal_bootstrap.showValidationMessage(`AHT minutes can't be zero (0).`)
                        }}
                        return {{ deal_name: deal_name, build_aht: build_aht, audit_aht: audit_aht, process: "{process.id}" }}
                    }}
                }}).then((result) => {{
                    $.ajax({{
                        type: "POST",
                        contentType: "application/json",
                        url: '/deal/add',
                        data: JSON.stringify(result["value"]),
                        success: function(response) {{ 
                            if(response["operation"]){{ 
                                swal_bootstrap.fire({{
                                    icon: 'success',
                                    title: 'Add Deal',
                                    text: 'Created ' + response["data"]["deal"]["name"] + ' (Deal) under ' + node.title + "."
                                }})
                                .then(() => {{
                                    window.location.href = window.location.href
                                }})
                            }}
                        }},
                        dataType: 'json'
                    }});
                }})
            }}
        }}]
}}""")

    for deal in deals:
        data.append(f"""{{
    n_value: 'deal_{deal.id}',
    n_title: '{deal.name} (Deal)',
    n_id: {deal_to_tree_id[deal.id]},
    n_parentid: {process_id_to_tree_id[deal.process_id]},
    n_checkStatus: true,
    n_elements: [
        {{
            icon: 'fa fa-puzzle-piece',
            title: 'Edit AHT',
            onClick: (node) => {{
                $.getJSON("/assets/aht/{deal.id}")
                .then(function(response, code){{
                    
                    if(!response["data"]){{
                        swal_bootstrap.fire({{
                            icon: 'success',
                            title: 'AHT Update',
                            text: `Error editing AHT for {deal.name} (Deal).`}})
                        return
                    }}
                    
                    swal_bootstrap.fire({{
                        title: 'Edit AHT ({deal.name}) (Deal)',
                        html: `
                        <div class="text-center">
                            <label for="build_aht">Build AHT</label>
                            <input type="number" min=1 id="build_aht" class="swal2-input" value="` + response["data"]["build"] + `">

                            <label for="audit_aht">Audit AHT</label>
                            <input type="number" min=1 id="audit_aht" class="swal2-input" value="` + response["data"]["audit"] + `">
                        </div>
                        `,
                        confirmButtonText: 'Save',
                        focusConfirm: false,
                        preConfirm: () => {{
                            var build_aht = Swal.getPopup().querySelector('#build_aht').value
                            var audit_aht = Swal.getPopup().querySelector('#audit_aht').value
                            if (!build_aht || !audit_aht) {{
                                swal_bootstrap.showValidationMessage(`AHT minutes can't be zero (0).`)
                            }}
                            return {{ build_aht: build_aht, audit_aht: audit_aht }}
                        }}
                    }}).then((result) => {{
                        
                        $.ajax({{
                            type: "POST",
                            contentType: "application/json",
                            url: '/aht/edit/{deal.id}',
                            data: JSON.stringify(result["value"]),
                            success: function(response) {{ 
                                if(response["operation"]){{ 
                                    swal_bootstrap.fire({{
                                        icon: 'success',
                                        title: 'AHT Update',
                                        text: 'Updated AHT for {deal.name} (Deal).'
                                    }})
                                }}
                            }},
                            dataType: 'json'
                        }});
                        
                        
                    }})
                }})
            }}
        }}]
}}""")

    return ", ".join(data)


@app.route('/aht_tree')
@login_required
def aht_tree():
    if flask_session["user"]['is_admin']:
        return render_template("tree.html", data=get_tree())


@app.route('/aht/edit/<id>', methods=["POST", "GET"])
@login_required
def edit_aht(id):
    if request.method == "POST":
        form_data = request.json
        print(form_data)
        check = AHT.query.get(id)
        if check:
            check.setter({"build": form_data["build_aht"], "audit": form_data["audit_aht"]})
            return {
                "operation": True
            }
    return {
        "operation": False
    }


@app.route('/assets/aht/<id>')
@login_required
def get_aht(id):
    check = AHT.query.get(id)
    if check:
        return {"data": check.as_dict()}
    return {"data": False}


@app.route('/process/add', methods=["POST", "GET"])
@login_required
def add_process():
    if request.method == "POST":
        form_data = request.json
        process = Process(form_data["process_name"], flask_session["user"]['username'], form_data["marketplace"])
        if process.id:
            return {"operation": True, "data": process.as_dict()}
        return {"operation": False, "data": False}
    return {"operation": False}


@app.route('/deal/add', methods=["POST", "GET"])
@login_required
def add_deal():
    if request.method == "POST":
        form_data = request.json
        deal = Deal(form_data["deal_name"], flask_session["user"]['username'], form_data["process"])
        if deal.id:
            aht = AHT(deal.id, form_data["build_aht"], form_data["audit_aht"], flask_session["user"]['username'])
            if aht.id:
                return {"operation": True, "data": {"deal": deal.as_dict(), "aht": aht.as_dict()}}
            return {"operation": False, "data": {"deal": deal.as_dict(), "aht": aht.as_dict()}}
        return {"operation": False, "data": False}
    return {"operation": False}


@app.route('/delete', methods=['POST'])
@login_required
def delete_prod_non_prod():
    if request.method == "POST":
        form_data = request.json["data"]

        if form_data["type"] == "non_prod":
            check = NonProd.query.get(form_data["id"])
        else:
            check = Prod.query.get(form_data["id"])

        if check:
            check.__delete__()
            return {"operation": True}
        return {"operation": False}


@app.route('/reports')
@login_required
def reports_consolidated():
    is_admin = flask_session["user"]['is_admin']
    prod_data = [d.as_dict() for d in Prod.query.all()]
    non_prod_data = [d.as_dict() for d in NonProd.query.all()]
    return render_template("reports.html", prod_data=prod_data, non_prod_data=non_prod_data, is_admin=is_admin)


@app.route('/prod/reports')
@login_required
def detailed_repot():
    data = [d.as_dict() for d in Prod.query.all()]
    return render_template("detailed_report.html", prod_data=data)


@app.route('/non_prod/reports')
@login_required
def report_non_pro():
    data = [d.as_dict() for d in NonProd.query.all()]
    return render_template("detailed_non_report.html", prod_data=data)


@app.route('/prod/edit/<id>', methods=["GET", "POST"])
@login_required
def edit_production(id):
    if flask_session["user"]['is_admin']:
        if request.method == "POST":
            form_json = request.json
            form_data = form_json["data"]
            #
            # fields_to_convert_to_int = ["marketplace", "process", "deal_name", "deal_count", "title_count",
            #                             "emails_count", "onsite_count", "pns_count",
            #                             "vendisto_count", "validation_count", "utilization"]
            # for field in fields_to_convert_to_int:
            #     if field in form_data:
            #         form_data[field] = int(form_data[field])

            form_data["marketplace_id"] = form_data.pop("marketplace")
            form_data["process_id"] = form_data.pop("process")

            form_data["build_audit_date"] = datetime.datetime.strptime(form_data["build_audit_date"], "%Y-%m-%d")
            form_data["live_date"] = datetime.datetime.strptime(form_data["live_date"], "%Y-%m-%d")
            check = Prod.query.get(id)
            print(form_data)
            if check:
                check.edit_setter(form_data)
                return {"operation": True}
            return {"operation": False}

        check = Prod.query.get(id)
        if check:
            check = check.as_dict()
        return render_template('edit_production.html', id=id, data=check)


@app.route('/non_prod/edit/<id>', methods=["GET", "POST"])
@login_required
def edit_non_production(id):
    if flask_session["user"]['is_admin']:
        if request.method == "POST":
            form_json = request.json
            form_data = form_json["data"]
            form_data["marketplace_id"] = form_data.pop("marketplace")
            form_data["type_id"] = form_data.pop("type")
            form_data["category_id"] = form_data.pop("category")

            print(form_data, id)

            form_data["work_date"] = datetime.datetime.strptime(form_data["work_date"], "%Y-%m-%d")

            check = NonProd.query.get(id)
            print(check)
            if check:
                check.edit_setter(form_data)
                return {"operation": True}
            return {"operation": False}
        check = NonProd.query.get(id)
        if check:
            check = check.as_dict()
        return render_template('edit_non_production.html', id=id, data=check,
                               marketplaces=[marketplace.as_dict() for marketplace in Marketplace.query.all()],
                               types=[type.as_dict() for type in NPType.query.all()],
                               categories=[category.as_dict() for category in NPCategory.query.all()])


@app.route('/prod/add', methods=["GET", "POST"])
@login_required
def add_prod():
    if request.method == "POST":
        form_data_list = request.json["data"]
        for form_data in form_data_list:
            form_data["build_audit_date"] = datetime.datetime.strptime(form_data["build_audit_date"], "%Y-%m-%d")
            form_data["live_date"] = datetime.datetime.strptime(form_data["live_date"], "%Y-%m-%d")
            form_data["created_by"] = "simmnu"
            entry = Prod(form_data["user_id"], form_data["build_audit"], form_data["build_audit_date"],
                         form_data["live_date"], form_data["marketplace"], form_data["process"], form_data["deal_name"],
                         form_data["deal_count"], form_data["sim"], form_data["title_count"], form_data["emails_count"],
                         form_data["onsite_count"], form_data["pns_count"], form_data["vendisto_count"],
                         form_data["validation_count"], form_data["utilization"], form_data["created_by"])
            if entry.id == None:
                return {'operation': False}
        return {'operation': True}

    return render_template('add_production.html')


@app.route('/non_prod/add', methods=["GET", "POST"])
@login_required
def add_non_prod():
    if request.method == "POST":
        form_data_list = request.json["data"]
        for form_data in form_data_list:
            form_data["work_date"] = datetime.datetime.strptime(form_data["work_date"], "%Y-%m-%d")
            form_data["created_by"] = "simmnu"
            entry = NonProd(form_data["user_id"], form_data["work_date"], form_data["marketplace"], form_data["type"],
                            form_data["category"], form_data["task_name"], form_data["time_taken"],
                            form_data["emails_count"], form_data["onsite_count"], form_data["pns_count"],
                            form_data["vendisto_count"], form_data["validation_count"], form_data["comments"],
                            form_data["created_by"])
            if entry.id is None:
                return {'operation': False}
        return {'operation': True}
    return render_template('add_non_production.html',
                           marketplaces=[marketplace.as_dict() for marketplace in Marketplace.query.all()],
                           types=[type.as_dict() for type in NPType.query.all()],
                           categories=[category.as_dict() for category in NPCategory.query.all()])


@app.route('/logout')
@login_required
@login_required
def logout():
    flask_session.pop('user')
    flash("Logged out.", "info")
    return redirect(url_for('login'))


app.run(host="0.0.0.0", port=5000, debug=True)
