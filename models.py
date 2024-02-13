from flask import Flask, jsonify, render_template, redirect, url_for, request, session as flask_session, flash, abort, \
    send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import datetime

app = Flask(__name__)
app.secret_key = '9110cbe934f6704a90863582e35c73e7'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsstand_.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://Books_prod:Zxcv!1234@ec2-54-70-46-145.us-west-2.compute.amazonaws.com:3306/prod'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)


# class BooksNonProdManagement(Base):
#     __tablename__ = 'books_non_prod_management'
#     SL_No = db.db.Column(db.db.Integer, primary_key=True, autoincrement=True, unique=True)
#     MarketPlace = db.Column(db.String)
#     Type = db.Column(db.String)
#     Category = db.Column(db.String)

class NonProd(db.Model):
    __tablename__ = 'non_prod'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    work_date = db.Column(db.Date)

    marketplace_id = db.Column(db.Integer, db.ForeignKey('marketplace.id'))
    marketplace = db.relationship("Marketplace", backref='non_prod_marketplace', lazy='subquery',
                                  foreign_keys=[marketplace_id])

    type_id = db.Column(db.Integer, db.ForeignKey('non_prod_type.id'))
    type = db.relationship("NPType", backref='non_prod_type', lazy='subquery', foreign_keys=[type_id])

    category_id = db.Column(db.Integer, db.ForeignKey('non_prod_category.id'))
    category = db.relationship("NPCategory", backref='non_prod_category', lazy='subquery', foreign_keys=[category_id])

    task_name = db.Column(db.String(75))
    time_taken = db.Column(db.Integer)
    emails_count = db.Column(db.Integer)
    onsite_count = db.Column(db.Integer)
    pns_count = db.Column(db.Integer)
    vendisto_count = db.Column(db.Integer)
    validation_count = db.Column(db.Integer)
    comments = db.Column(db.String(500))
    created_by = db.Column(db.String(50))
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        dict_data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        dict_data["marketplace"] = self.marketplace.name
        dict_data["type"] = self.type.name
        dict_data["category"] = self.category.name
        return dict_data

    def __repr__(self):
        return '<NonProd %r>' % self.id

    def __delete__(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            print(e)
            return

    def __init__(self, user_id, work_date, marketplace_id, type_id, category_id, task_name, time_taken, emails_count,
                 onsite_count, pns_count, vendisto_count, validation_count, comments, created_by):
        self.user_id = user_id
        self.work_date = work_date
        self.marketplace_id = marketplace_id
        self.type_id = type_id
        self.category_id = category_id
        self.task_name = task_name
        self.time_taken = time_taken
        self.emails_count = emails_count
        self.onsite_count = onsite_count
        self.pns_count = pns_count
        self.vendisto_count = vendisto_count
        self.validation_count = validation_count
        self.comments = comments
        self.created_by = created_by

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created non_prod for {work_date}."
        except:
            return False, f"Error non_prod {work_date}."

    def setter(self, data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Setter non_prod for {self.id}."
        except:
            return False, f"Error non_prod {self.id}."

    def edit_setter(self, data):
        for k, v in data.items():
            if hasattr(self, k):
                try:
                    setattr(self, k, v)
                except:
                    print(k, v)
        try:
            db.session.commit()
            return self, f"Setter non_prod for {self.id}."
        except:
            return False, f"Error non_prod {self.id}."


class Prod(db.Model):
    __tablename__ = 'prod'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50))
    build_audit = db.Column(db.String(50))
    build_audit_date = db.Column(db.Date)
    live_date = db.Column(db.Date)

    marketplace_id = db.Column(db.Integer, db.ForeignKey('marketplace.id'))
    marketplace = db.relationship("Marketplace", backref='prod_marketplace', lazy='subquery',
                                  foreign_keys=[marketplace_id])

    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    process = db.relationship("Process", backref='prod_process', lazy='subquery', foreign_keys=[process_id])

    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'))
    deal = db.relationship("Deal", backref='prod_deal', lazy='subquery', foreign_keys=[deal_id])

    deal_count = db.Column(db.Integer)
    sim = db.Column(db.String(150))
    title_count = db.Column(db.Integer)
    emails_count = db.Column(db.Integer)
    onsite_count = db.Column(db.Integer)
    pns_count = db.Column(db.Integer)
    vendisto_count = db.Column(db.Integer)
    validation_count = db.Column(db.Integer)
    utilization = db.Column(db.Integer)
    created_by = db.Column(db.String(50))
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        dict_data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        dict_data["marketplace"] = self.marketplace.name
        dict_data["process"] = self.process.name
        dict_data["deal_name"] = self.deal.name
        return dict_data

    def __repr__(self):
        return '<Prod %r>' % self.id

    def __delete__(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            return

    def __init__(self, user_id, build_audit, build_audit_date, live_date, marketplace_id, process_id, deal_id,
                 deal_count, sim, title_count, emails_count, onsite_count, pns_count, vendisto_count, validation_count,
                 utilization, created_by):
        self.user_id = user_id
        self.build_audit = build_audit
        self.build_audit_date = build_audit_date
        self.live_date = live_date
        self.marketplace_id = marketplace_id
        self.process_id = process_id
        self.deal_id = deal_id
        self.deal_count = deal_count
        self.sim = sim
        self.title_count = title_count
        self.emails_count = emails_count
        self.onsite_count = onsite_count
        self.pns_count = pns_count
        self.vendisto_count = vendisto_count
        self.validation_count = validation_count
        self.utilization = utilization
        self.created_by = created_by

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created prod for {build_audit_date}."
        except Exception as e:
            print(f"{e}")
            return False, f"Error prod {build_audit_date}."

    def setter(self, data):
        for k, v in data.items():
            if hasattr(self, k):
                setattr(self, k, v)
        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Setter prod for {self.id}."
        except:
            return False, f"Error prod {self.id}."
    def edit_setter(self, data):
        for k, v in data.items():
            if hasattr(self, k):
                try:
                    setattr(self, k, v)
                except:
                    print(k,v)
        try:
            db.session.commit()
            return self, f"Setter prod for {self.id}."
        except:
            return False, f"Error prod {self.id}."

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    is_admin = db.Column(db.Boolean())
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def __init__(self, username, password, firstname, lastname, is_admin):
        self.username = username
        self.set_password(password)
        self.firstname = firstname
        self.lastname = lastname
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % self.username


# TODO: Add dropdowns


class Marketplace(db.Model):
    __tablename__ = "marketplace"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    created_by = db.Column(db.String(50))
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<Marketplace %r>' % self.name

    def __delete__(self):
        try:
            self.delete()
            db.session.commit()
            return True
        except:
            return

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created marketplace for {name}."
        except:
            return False, f"Error marketplace {name}."


class Process(db.Model):
    __tablename__ = "process"

    marketplace_id = db.Column(db.Integer, db.ForeignKey('marketplace.id'))
    marketplace = db.relationship("Marketplace", backref='process_marketplace', lazy='subquery',
                                  foreign_keys=[marketplace_id])

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_by = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<Process %r>' % self.name

    def __delete__(self):
        try:
            self.delete()
            db.session.commit()
            return True
        except:
            return

    def __init__(self, name, created_by, marketplace_id):
        self.name = name
        self.created_by = created_by
        self.marketplace_id = marketplace_id

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created process for {name}."
        except:
            return False, f"Error process {name}."


class Deal(db.Model):
    __tablename__ = "deal"

    process_id = db.Column(db.Integer, db.ForeignKey('process.id'))
    process = db.relationship("Process", backref='deal_process', lazy='subquery', foreign_keys=[process_id])

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_by = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __delete__(self):
        try:
            self.delete()
            db.session.commit()
            return True
        except:
            return

    def __repr__(self):
        return '<Deal %r>' % self.name

    def __init__(self, name, created_by, process_id):
        self.name = name
        self.created_by = created_by
        self.process_id = process_id

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created deal for {name}."
        except:
            return False, f"Error deal {name}."


class NPType(db.Model):
    __tablename__ = "non_prod_type"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_by = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __delete__(self):
        try:
            self.delete()
            db.session.commit()
            return True
        except:
            return

    def __repr__(self):
        return '<NPType %r>' % self.name

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created non_prod_type for {name}."
        except:
            return False, f"Error non_prod_type {name}."


class NPCategory(db.Model):
    __tablename__ = "non_prod_category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    created_by = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __delete__(self):
        try:
            self.delete()
            db.session.commit()
            return True
        except:
            return

    def __repr__(self):
        return '<NPCategory %r>' % self.name

    def __init__(self, name, created_by):
        self.name = name
        self.created_by = created_by

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created non_prod_category for {name}."
        except:
            return False, f"Error non_prod_category {name}."


class AHT(db.Model):
    __tablename__ = "aht"
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'))
    deal = db.relationship("Deal", backref='aht_deal', lazy='subquery', foreign_keys=[deal_id])

    id = db.Column(db.Integer, primary_key=True)
    build = db.Column(db.Integer)
    audit = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    created_on = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow())

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __delete__(self):
        try:
            self.delete()
            db.session.commit()
            return True
        except:
            return

    def __repr__(self):
        return '<AHT %r>' % self.name

    def __init__(self, deal_id, build, audit, created_by):
        self.deal_id = deal_id
        self.build = build
        self.audit = audit
        self.created_by = created_by

        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Created aht for {self.deal_id}."
        except:
            return False, f"Error aht {self.deal_id}."

    def setter(self, data):
        for k, v in data.items():
            if hasattr(self, k):
                if k != ["id", "created_by", "created_on"]:
                    setattr(self, k, v)
        try:
            db.session.add(self)
            db.session.commit()
            return self, f"Setter aht for {self.id}."
        except:
            return False, f"Error aht {self.id}."


app.app_context().push()
db.create_all()

# ? Testing
# Marketplace("US", "simmnu")
# Marketplace("SG", "simmnu")
# Marketplace("NPT", "simmnu")
# Marketplace("MX_CT", "simmnu")
# Marketplace("JP", "simmnu")
# Marketplace("IT", "simmnu")
# Marketplace("FR", "simmnu")
# Marketplace("EU_5", "simmnu")
# Marketplace("ES", "simmnu")
# Marketplace("Design", "simmnu")
# Marketplace("CA", "simmnu")
# Marketplace("BR", "simmnu")
# Marketplace("AU", "simmnu")

#
# Process("US_KDP","simmnu",1)

#Deal("","simmnu",1)

# NPType("Ad-Hoc", "simmnu")
# NPType("Report","simmnu")
# NPType("Meeting","simmnu")
# NPType("Line up","simmnu")
# NPType("Training","simmnu")
# NPType("Leave","simmnu")
# NPType("Re-work","simmnu")
# NPType("Secondary Audit","simmnu")
# NPType("Pre QA","simmnu")
# NPType("Design","simmnu")
#

# NPCategory("US_KDP","simmnu")
# NPCategory("Comixology","simmnu")
# NPCategory("US_Kindlecomics","simmnu")
# NPCategory("UK_Kindlecomics","simmnu")
# NPCategory("US_APUB","simmnu")
# NPCategory("Specialty_reading","simmnu")
# NPCategory("US_ABR","simmnu")
# NPCategory("US_KindleRecaps","simmnu")
# NPCategory("US_KindleRewards","simmnu")
# NPCategory("Design","simmnu")
# NPCategory("Indie","simmnu")
# NPCategory("CA_NA_Deals","simmnu")
# NPCategory("CA_KDP","simmnu")
# NPCategory("SG_Merch","simmnu")
# NPCategory("SG_Books","simmnu")
# NPCategory("SG_Books_VG","simmnu")
# NPCategory("NA_Merch","simmnu")
# NPCategory("BR_Merch","simmnu")
# NPCategory("Ebooks","simmnu")
# NPCategory("Pbooks","simmnu")
# NPCategory("ABR","simmnu")
# NPCategory("Device","simmnu")
# NPCategory("Paid_Marketing","simmnu")
# NPCategory("FR_KDP","simmnu")
# NPCategory("AU_KDP","simmnu")
# NPCategory("UK_KDP","simmnu")
# NPCategory("MXCT_NA_Deals","simmnu")
# NPCategory("MX_KDP","simmnu")
# NPCategory("CT_KDP","simmnu")
# NPCategory("DE_KDP","simmnu")
# NPCategory("IT_KDP","simmnu")
# NPCategory("ES_KDP","simmnu")
# NPCategory("NPT","simmnu")
# NPCategory("IN merch","simmnu")
# NPCategory("ART","simmnu")


# AHT(145,40,20,"simmnu")
# AHT(106,30,10,"simmnu")
# AHT(283,30,15,"simmnu")
# AHT(113,5,0,"simmnu")
# AHT(290,5,0,"simmnu")
# AHT(25,20,10,"simmnu")
# AHT(107,20,10,"simmnu")
# AHT(284,20,10,"simmnu")
# AHT(295,30,10,"simmnu")
# AHT(28,0,0,"simmnu")
# AHT(27,50,25,"simmnu")
# AHT(109,50,25,"simmnu")
# AHT(286,50,25,"simmnu")
# AHT(26,15,7.5,"simmnu")
# AHT(108,15,5,"simmnu")
# AHT(285,15,5,"simmnu")
# AHT(114,60,30,"simmnu")
# AHT(291,60,15,"simmnu")
# AHT(115,300,150,"simmnu")
# AHT(292,300,150,"simmnu")
# AHT(180,20,10,"simmnu")
# AHT(47,45,22.5,"simmnu")
# AHT(155,0,0,"simmnu")
# AHT(222,30,15,"simmnu")
# AHT(223,30,15,"simmnu")
# AHT(84,10,10,"simmnu")
# AHT(191,10,5,"simmnu")
# AHT(181,30,15,"simmnu")
# AHT(182,0,0,"simmnu")
# AHT(90,30,30,"simmnu")
# AHT(196,30,15,"simmnu")
# AHT(1,30,15,"simmnu")
# AHT(312,30,15,"simmnu")
# AHT(49,90,45,"simmnu")
# AHT(2,150,75,"simmnu")
# AHT(50,30,15,"simmnu")
# AHT(224,0,0,"simmnu")
# AHT(262,20,10,"simmnu")
# AHT(54,30,15,"simmnu")
# AHT(56,30,15,"simmnu")
# AHT(55,30,15,"simmnu")
# AHT(3,120,60,"simmnu")
# AHT(46,30,15,"simmnu")
# AHT(4,30,0,"simmnu")
# AHT(48,30,15,"simmnu")
# AHT(63,60,30,"simmnu")
# AHT(5,90,45,"simmnu")
# AHT(53,30,15,"simmnu")
# AHT(249,20,10,"simmnu")
# AHT(24,30,15,"simmnu")
# AHT(6,60,30,"simmnu")
# AHT(296,90,45,"simmnu")
# AHT(65,120,60,"simmnu")
# AHT(328,20,0,"simmnu")
# AHT(148,20,10,"simmnu")
# AHT(131,30,15,"simmnu")
# AHT(139,30,15,"simmnu")
# AHT(293,1.5,1,"simmnu")
# AHT(298,20,10,"simmnu")
# AHT(299,5,0,"simmnu")
# AHT(303,30,15,"simmnu")
# AHT(302,30,15,"simmnu")
# AHT(300,20,10,"simmnu")
# AHT(301,5,0,"simmnu")
# AHT(322,30,15,"simmnu")
# AHT(332,20,10,"simmnu")
# AHT(45,15,10,"simmnu")
# AHT(156,4,2,"simmnu")
# AHT(79,30,5,"simmnu")
# AHT(125,30,15,"simmnu")
# AHT(157,10,5,"simmnu")
# AHT(176,120,60,"simmnu")
# AHT(325,15,7.5,"simmnu")
# AHT(319,10,5,"simmnu")
# AHT(320,10,5,"simmnu")
# AHT(202,15,7.5,"simmnu")
# AHT(121,30,15,"simmnu")
# AHT(120,30,15,"simmnu")
# AHT(122,30,15,"simmnu")
# AHT(123,30,15,"simmnu")
# AHT(40,30,0,"simmnu")
# AHT(42,15,10,"simmnu")
# AHT(41,15,10,"simmnu")
# AHT(39,30,15,"simmnu")
# AHT(7,50,25,"simmnu")
# AHT(304,3,1.5,"simmnu")
# AHT(324,10,5,"simmnu")
# AHT(225,0,0,"simmnu")
# AHT(174,30,15,"simmnu")
# AHT(133,30,15,"simmnu")
# AHT(143,30,15,"simmnu")
# AHT(280,30,15,"simmnu")
# AHT(282,120,60,"simmnu")
# AHT(183,0,0,"simmnu")
# AHT(127,120,60,"simmnu")
# AHT(152,120,60,"simmnu")
# AHT(154,120,60,"simmnu")
# AHT(178,120,60,"simmnu")
# AHT(221,120,60,"simmnu")
# AHT(253,120,60,"simmnu")
# AHT(66,60,30,"simmnu")
# AHT(126,30,30,"simmnu")
# AHT(151,30,15,"simmnu")
# AHT(153,30,15,"simmnu")
# AHT(177,30,15,"simmnu")
# AHT(220,30,30,"simmnu")
# AHT(252,30,60,"simmnu")
# AHT(67,30,15,"simmnu")
# AHT(68,120,60,"simmnu")
# AHT(93,120,60,"simmnu")
# AHT(179,0,0,"simmnu")
# AHT(158,20,10,"simmnu")
# AHT(159,20,0,"simmnu")
# AHT(329,2,1,"simmnu")
# AHT(103,4.5,0,"simmnu")
# AHT(102,0.5,0,"simmnu")
# AHT(226,30,15,"simmnu")
# AHT(265,20,10,"simmnu")
# AHT(277,120,60,"simmnu")
# AHT(264,60,30,"simmnu")
# AHT(69,60,30,"simmnu")
# AHT(307,60,10,"simmnu")
# AHT(8,20,0,"simmnu")
# AHT(327,30,0,"simmnu")
# AHT(70,40,20,"simmnu")
# AHT(278,60,30,"simmnu")
# AHT(274,20,10,"simmnu")
# AHT(168,90,45,"simmnu")
# AHT(173,30,0,"simmnu")
# AHT(270,60,30,"simmnu")
# AHT(184,30,15,"simmnu")
# AHT(185,30,45,"simmnu")
# AHT(227,75,37.5,"simmnu")
# AHT(305,3,1,"simmnu")
# AHT(306,3,1,"simmnu")
# AHT(130,360,180,"simmnu")
# AHT(138,360,180,"simmnu")
# AHT(140,40,20,"simmnu")
# AHT(276,60,30,"simmnu")
# AHT(228,40,20,"simmnu")
# AHT(203,5,2.5,"simmnu")
# AHT(321,10,5,"simmnu")
# AHT(204,15,7.5,"simmnu")
# AHT(229,60,30,"simmnu")
# AHT(119,30,0,"simmnu")
# AHT(35,30,15,"simmnu")
# AHT(101,30,15,"simmnu")
# AHT(251,20,10,"simmnu")
# AHT(165,90,30,"simmnu")
# AHT(201,60,30,"simmnu")
# AHT(81,150,100,"simmnu")
# AHT(188,150,75,"simmnu")
# AHT(88,120,60,"simmnu")
# AHT(194,120,60,"simmnu")
# AHT(111,60,30,"simmnu")
# AHT(288,60,30,"simmnu")
# AHT(175,90,45,"simmnu")
# AHT(166,40,20,"simmnu")
# AHT(256,20,10,"simmnu")
# AHT(230,120,60,"simmnu")
# AHT(231,150,75,"simmnu")
# AHT(254,30,15,"simmnu")
# AHT(268,200,100,"simmnu")
# AHT(260,30,15,"simmnu")
# AHT(258,300,150,"simmnu")
# AHT(267,120,60,"simmnu")
# AHT(255,10,5,"simmnu")
# AHT(259,1,0.5,"simmnu")
# AHT(245,20,10,"simmnu")
# AHT(246,20,10,"simmnu")
# AHT(247,20,10,"simmnu")
# AHT(186,15,10,"simmnu")
# AHT(9,90,45,"simmnu")
# AHT(10,30,15,"simmnu")
# AHT(11,60,30,"simmnu")
# AHT(232,30,15,"simmnu")
# AHT(261,30,15,"simmnu")
# AHT(311,30,15,"simmnu")
# AHT(31,1,0.5,"simmnu")
# AHT(62,1,0.5,"simmnu")
# AHT(94,1,0.5,"simmnu")
# AHT(248,1,0.5,"simmnu")
# AHT(82,20,15,"simmnu")
# AHT(189,20,15,"simmnu")
# AHT(326,20,10,"simmnu")
# AHT(96,50,25,"simmnu")
# AHT(198,50,25,"simmnu")
# AHT(273,15,7.5,"simmnu")
# AHT(206,15,7.5,"simmnu")
# AHT(86,20,20,"simmnu")
# AHT(192,20,10,"simmnu")
# AHT(205,15,7.5,"simmnu")
# AHT(269,30,15,"simmnu")
# AHT(58,30,15,"simmnu")
# AHT(12,60,30,"simmnu")
# AHT(144,3,1.5,"simmnu")
# AHT(110,180,90,"simmnu")
# AHT(287,180,90,"simmnu")
# AHT(51,30,15,"simmnu")
# AHT(61,30,15,"simmnu")
# AHT(207,15,7.5,"simmnu")
# AHT(80,90,45,"simmnu")
# AHT(52,30,15,"simmnu")
# AHT(16,2,0,"simmnu")
# AHT(97,100,50,"simmnu")
# AHT(199,100,50,"simmnu")
# AHT(83,150,75,"simmnu")
# AHT(190,150,75,"simmnu")
# AHT(149,20,10,"simmnu")
# AHT(150,20,10,"simmnu")
# AHT(87,60,30,"simmnu")
# AHT(193,60,30,"simmnu")
# AHT(85,50,25,"simmnu")
# AHT(116,50,25,"simmnu")
# AHT(294,50,25,"simmnu")
# AHT(310,50,25,"simmnu")
# AHT(318,10,0,"simmnu")
# AHT(317,20,10,"simmnu")
# AHT(314,30,15,"simmnu")
# AHT(272,60,30,"simmnu")
# AHT(89,480,0,"simmnu")
# AHT(195,480,0,"simmnu")
# AHT(313,480,240,"simmnu")
# AHT(233,240,120,"simmnu")
# AHT(234,300,150,"simmnu")
# AHT(57,30,15,"simmnu")
# AHT(38,40,20,"simmnu")
# AHT(146,20,10,"simmnu")
# AHT(91,100,75,"simmnu")
# AHT(197,100,50,"simmnu")
# AHT(128,20,10,"simmnu")
# AHT(141,20,10,"simmnu")
# AHT(95,150,75,"simmnu")
# AHT(169,90,0,"simmnu")
# AHT(33,30,15,"simmnu")
# AHT(99,30,15,"simmnu")
# AHT(208,15,7.5,"simmnu")
# AHT(209,15,7.5,"simmnu")
# AHT(210,15,7.5,"simmnu")
# AHT(339,15,7.5,"simmnu")
# AHT(338,10,5,"simmnu")
# AHT(235,10,5,"simmnu")
# AHT(211,15,7.5,"simmnu")
# AHT(331,15,7.5,"simmnu")
# AHT(212,15,7.5,"simmnu")
# AHT(330,5,2.5,"simmnu")
# AHT(213,15,7.5,"simmnu")
# AHT(161,10,5,"simmnu")
# AHT(257,60,30,"simmnu")
# AHT(78,25,12.5,"simmnu")
# AHT(333,60,30,"simmnu")
# AHT(309,20,10,"simmnu")
# AHT(236,0,0,"simmnu")
# AHT(237,0,0,"simmnu")
# AHT(238,0,0,"simmnu")
# AHT(239,0,0,"simmnu")
# AHT(240,0,0,"simmnu")
# AHT(13,30,0,"simmnu")
# AHT(214,15,7.5,"simmnu")
# AHT(135,45,22.5,"simmnu")
# AHT(340,30,15,"simmnu")
# AHT(92,30,15,"simmnu")
# AHT(241,60,30,"simmnu")
# AHT(75,60,30,"simmnu")
# AHT(14,10,5,"simmnu")
# AHT(281,20,10,"simmnu")
# AHT(308,15,5,"simmnu")
# AHT(134,120,60,"simmnu")
# AHT(137,60,30,"simmnu")
# AHT(136,500,250,"simmnu")
# AHT(147,240,120,"simmnu")
# AHT(30,60,30,"simmnu")
# AHT(215,20,10,"simmnu")
# AHT(29,30,15,"simmnu")
# AHT(275,60,30,"simmnu")
# AHT(263,40,20,"simmnu")
# AHT(21,120,60,"simmnu")
# AHT(187,120,60,"simmnu")
# AHT(242,10,5,"simmnu")
# AHT(266,360,180,"simmnu")
# AHT(72,120,60,"simmnu")
# AHT(160,120,60,"simmnu")
# AHT(76,30,15,"simmnu")
# AHT(73,20,10,"simmnu")
# AHT(15,20,0,"simmnu")
# AHT(104,2.24,0,"simmnu")
# AHT(216,5,2.5,"simmnu")
# AHT(217,15,7.5,"simmnu")
# AHT(218,15,7.5,"simmnu")
# AHT(335,15,7.5,"simmnu")
# AHT(337,15,7.5,"simmnu")
# AHT(334,10,5,"simmnu")
# AHT(336,10,5,"simmnu")
# AHT(64,20,10,"simmnu")
# AHT(17,20,10,"simmnu")
# AHT(18,20,10,"simmnu")
# AHT(105,15,0,"simmnu")
# AHT(59,30,15,"simmnu")
# AHT(19,20,10,"simmnu")
# AHT(43,40,20,"simmnu")
# AHT(44,15,10,"simmnu")
# AHT(243,60,0,"simmnu")
# AHT(323,20,10,"simmnu")
# AHT(132,45,22.5,"simmnu")
# AHT(142,45,20,"simmnu")
# AHT(60,30,15,"simmnu")
# AHT(297,90,45,"simmnu")
# AHT(162,10,5,"simmnu")
# AHT(315,40,20,"simmnu")
# AHT(316,60,30,"simmnu")
# AHT(163,30,15,"simmnu")
# AHT(129,60,30,"simmnu")
# AHT(170,120,60,"simmnu")
# AHT(167,60,30,"simmnu")
# AHT(279,0,0,"simmnu")
# AHT(98,15,7.5,"simmnu")
# AHT(200,15,7.5,"simmnu")
# AHT(164,10,5,"simmnu")
# AHT(77,30,15,"simmnu")
# AHT(20,0,0,"simmnu")
# AHT(71,30,15,"simmnu")
# AHT(250,20,10,"simmnu")
# AHT(271,30,15,"simmnu")
# AHT(22,20,10,"simmnu")
# AHT(117,30,0,"simmnu")
# AHT(34,30,15,"simmnu")
# AHT(100,30,15,"simmnu")
# AHT(112,300,150,"simmnu")
# AHT(289,300,20,"simmnu")
# AHT(219,0,0,"simmnu")
# AHT(124,30,15,"simmnu")
# AHT(244,30,15,"simmnu")
# AHT(171,180,90,"simmnu")
# AHT(172,80,40,"simmnu")
# AHT(36,30,15,"simmnu")
# AHT(118,30,0,"simmnu")
# AHT(74,20,10,"simmnu")
# AHT(23,35,15,"simmnu")
# AHT(37,40,20,"simmnu")
# AHT(32,30,15,"simmnu")



# AHT(93, 120, 60, "simmnu")
# AHT(94, 120, 60, "simmnu")
# AHT(4, 15, 7.5, "simmnu")
# AHT(5, 5, 2.5, "simmnu")
# AHT(6, 15, 7.5, "simmnu")
# AHT(7, 15, 7.5, "simmnu")
# AHT(8, 15, 7.5, "simmnu")
# AHT(9, 15, 7.5, "simmnu")
# AHT(10, 15, 7.5, "simmnu")
# AHT(11, 15, 7.5, "simmnu")
# AHT(12, 15, 7.5, "simmnu")
# AHT(13, 15, 7.5, "simmnu")
# AHT(14, 15, 7.5, "simmnu")
# AHT(15, 15, 7.5, "simmnu")
# AHT(16, 15, 7.5, "simmnu")
# AHT(17, 20, 10, "simmnu")
# AHT(18, 5, 2.5, "simmnu")
# AHT(19, 15, 7.5, "simmnu")
# AHT(20, 15, 7.5, "simmnu")
# AHT(21, 0, 0, "simmnu")
# AHT(56, 480, 240, "simmnu")
# AHT(22, 30, 15, "simmnu")
# AHT(23, 40, 20, "simmnu")
# AHT(24, 60, 30, "simmnu")
# AHT(25, 20, 10, "simmnu")
# AHT(26, 10, 0, "simmnu")
# AHT(27, 10, 5, "simmnu")
# AHT(28, 10, 5, "simmnu")
# AHT(29, 10, 5, "simmnu")
# AHT(30, 30, 15, "simmnu")
# AHT(31, 20, 10, "simmnu")
# AHT(32, 10, 5, "simmnu")
# AHT(33, 15, 7.5, "simmnu")
# AHT(34, 20, 10, "simmnu")
# AHT(35, 30, 0, "simmnu")
# AHT(36, 20, 0, "simmnu")
# AHT(37, 2, 1, "simmnu")
# AHT(38, 5, 2.5, "simmnu")
# AHT(39, 15, 7.5, "simmnu")
# AHT(40, 20, 10, "simmnu")
# AHT(41, 60, 30, "simmnu")
# AHT(42, 20, 10, "simmnu")
# AHT(43, 30, 15, "simmnu")
# AHT(44, 0, 0, "simmnu")
# AHT(45, 0, 0, "simmnu")
# AHT(46, 30, 15, "simmnu")
# AHT(46, 90, 45, "simmnu")
# AHT(48, 15, 10, "simmnu")
# AHT(49, 150, 75, "simmnu")
# AHT(34, 30, 15, "simmnu")
# AHT(51, 150, 75, "simmnu")
# AHT(2, 10, 5, "simmnu")
# AHT(53, 20, 10, "simmnu")
# AHT(54, 60, 30, "simmnu")
# AHT(55, 120, 60, "simmnu")
# AHT(56, 0, 0, "simmnu")
# AHT(57, 30, 15, "simmnu")
# AHT(58, 100, 50, "simmnu")
# AHT(59, 50, 25, "simmnu")
# AHT(60, 100, 50, "simmnu")
# AHT(61, 15, 7.5, "simmnu")
# AHT(62, 60, 30, "simmnu")
# AHT(63, 30, 15, "simmnu")
# AHT(64, 20, 10, "simmnu")
# AHT(65, 15, 5, "simmnu")
# AHT(66, 50, 25, "simmnu")
# AHT(67, 180, 90, "simmnu")
# AHT(68, 60, 30, "simmnu")
# AHT(69, 300, 150, "simmnu")
# AHT(70, 5, 0, "simmnu")
# AHT(71, 30, 15, "simmnu")
# AHT(72, 300, 150, "simmnu")
# AHT(73, 1.5, 1, "simmnu")
# AHT(74, 50, 25, "simmnu")
# AHT(75, 30, 10, "simmnu")
# AHT(76, 90, 45, "simmnu")
# AHT(77, 90, 45, "simmnu")
# AHT(78, 20, 10, "simmnu")
# AHT(79, 5, 0, "simmnu")
# AHT(80, 20, 10, "simmnu")
# AHT(81, 5, 0, "simmnu")
# AHT(82, 30, 15, "simmnu")
# AHT(83, 5, 1.5, "simmnu")
# AHT(84, 1.5, 0.5, "simmnu")
# AHT(85, 20, 10, "simmnu")
# AHT(86, 15, 5, "simmnu")
# AHT(87, 20, 10, "simmnu")
# AHT(74, 50, 25, "simmnu")
# AHT(89, 30, 15, "simmnu")
# AHT(90, 30, 15, "simmnu")
# AHT(91, 120, 60, "simmnu")
# AHT(92, 0, 0, "simmnu")
# AHT(93, 120, 60, "simmnu")
# AHT(94, 120, 60, "simmnu")
# AHT(95, 0, 0, "simmnu")
# AHT(96, 4, 2, "simmnu")
# AHT(97, 10, 5, "simmnu")
# AHT(98, 20, 10, "simmnu")
# AHT(99, 20, 0, "simmnu")
# AHT(100, 120, 60, "simmnu")
# AHT(101, 10, 5, "simmnu")
# AHT(102, 10, 5, "simmnu")
# AHT(103, 30, 15, "simmnu")
# AHT(104, 10, 5, "simmnu")
# AHT(105, 90, 30, "simmnu")
# AHT(106, 40, 20, "simmnu")
# AHT(107, 60, 30, "simmnu")
# AHT(108, 90, 45, "simmnu")
# AHT(109, 90, 0, "simmnu")
# AHT(110, 120, 60, "simmnu")
# AHT(111, 180, 90, "simmnu")
# AHT(112, 80, 40, "simmnu")
# AHT(113, 30, 0, "simmnu")
# AHT(114, 30, 15, "simmnu")
# AHT(115, 90, 45, "simmnu")
# AHT(116, 120, 60, "simmnu")
# AHT(93, 120, 60, "simmnu")
# AHT(94, 120, 60, "simmnu")
# AHT(119, 30, 15, "simmnu")
# AHT(120, 30, 15, "simmnu")
# AHT(121, 0, 0, "simmnu")
# AHT(122, 0, 0, "simmnu")
# AHT(123, 30, 15, "simmnu")
# AHT(124, 75, 37.5, "simmnu")
# AHT(125, 40, 20, "simmnu")
# AHT(126, 60, 30, "simmnu")
# AHT(127, 120, 60, "simmnu")
# AHT(128, 150, 75, "simmnu")
# AHT(129, 30, 15, "simmnu")
# AHT(130, 240, 120, "simmnu")
# AHT(131, 300, 150, "simmnu")
# AHT(132, 10, 5, "simmnu")
# AHT(133, 0, 0, "simmnu")
# AHT(134, 0, 0, "simmnu")
# AHT(135, 0, 0, "simmnu")
# AHT(136, 0, 0, "simmnu")
# AHT(137, 0, 0, "simmnu")
# AHT(138, 60, 30, "simmnu")
# AHT(139, 10, 5, "simmnu")
# AHT(140, 60, 0, "simmnu")
# AHT(141, 30, 15, "simmnu")
# AHT(142, 20, 10, "simmnu")
# AHT(143, 20, 10, "simmnu")
# AHT(144, 20, 10, "simmnu")
# AHT(145, 1, 0.5, "simmnu")
# AHT(146, 20, 10, "simmnu")
# AHT(147, 20, 10, "simmnu")
# AHT(148, 20, 10, "simmnu")
# AHT(93, 120, 60, "simmnu")
# AHT(94, 120, 60, "simmnu")
# AHT(151, 30, 15, "simmnu")
# AHT(152, 10, 5, "simmnu")
# AHT(153, 20, 10, "simmnu")
# AHT(154, 60, 30, "simmnu")
# AHT(155, 300, 150, "simmnu")
# AHT(156, 1, 0.5, "simmnu")
# AHT(157, 30, 15, "simmnu")
# AHT(158, 30, 15, "simmnu")
# AHT(159, 20, 10, "simmnu")
# AHT(160, 40, 20, "simmnu")
# AHT(161, 60, 30, "simmnu")
# AHT(162, 20, 10, "simmnu")
# AHT(163, 360, 180, "simmnu")
# AHT(164, 120, 60, "simmnu")
# AHT(165, 200, 100, "simmnu")
# AHT(166, 30, 15, "simmnu")
# AHT(167, 60, 30, "simmnu")
# AHT(168, 30, 15, "simmnu")
# AHT(169, 60, 30, "simmnu")
# AHT(170, 15, 7.5, "simmnu")
# AHT(171, 20, 10, "simmnu")
# AHT(172, 60, 30, "simmnu")
# AHT(173, 60, 30, "simmnu")
# AHT(174, 120, 60, "simmnu")
# AHT(175, 60, 30, "simmnu")
# AHT(176, 0, 0, "simmnu")
# AHT(177, 30, 15, "simmnu")
# AHT(178, 20, 10, "simmnu")
# AHT(93, 120, 60, "simmnu")
# AHT(94, 120, 60, "simmnu")
# AHT(181, 20, 10, "simmnu")
# AHT(182, 20, 10, "simmnu")
# AHT(183, 20, 10, "simmnu")
# AHT(184, 360, 180, "simmnu")
# AHT(185, 60, 30, "simmnu")
# AHT(186, 45, 22.5, "simmnu")
# AHT(187, 20, 10, "simmnu")
# AHT(188, 300, 150, "simmnu")
# AHT(189, 45, 22.5, "simmnu")
# AHT(190, 500, 250, "simmnu")
# AHT(191, 60, 30, "simmnu")
# AHT(184, 360, 180, "simmnu")
# AHT(185, 40, 20, "simmnu")
# AHT(194, 40, 20, "simmnu")
# AHT(183, 20, 10, "simmnu")
# AHT(186, 45, 20, "simmnu")
# AHT(187, 60, 30, "simmnu")
# AHT(198, 3, 1.5, "simmnu")
# AHT(199, 40, 20, "simmnu")
# AHT(200, 20, 10, "simmnu")
# AHT(201, 240, 120, "simmnu")
# AHT(202, 20, 10, "simmnu")
# AHT(203, 30, 15, "simmnu")
# AHT(93, 120, 60, "simmnu")
# AHT(94, 120, 60, "simmnu")
# AHT(90, 30, 15, "simmnu")
# AHT(207, 150, 75, "simmnu")
# AHT(208, 120, 60, "simmnu")
# AHT(209, 30, 0, "simmnu")
# AHT(210, 90, 45, "simmnu")
# AHT(211, 60, 30, "simmnu")
# AHT(212, 50, 25, "simmnu")
# AHT(213, 20, 0, "simmnu")
# AHT(214, 90, 45, "simmnu")
# AHT(215, 30, 15, "simmnu")
# AHT(216, 60, 30, "simmnu")
# AHT(217, 60, 30, "simmnu")
# AHT(218, 30, 0, "simmnu")
# AHT(219, 10, 5, "simmnu")
# AHT(220, 20, 0, "simmnu")
# AHT(221, 20, 10, "simmnu")
# AHT(222, 20, 10, "simmnu")
# AHT(223, 20, 10, "simmnu")
# AHT(224, 0, 0, "simmnu")
# AHT(225, 20, 10, "simmnu")
# AHT(226, 35, 15, "simmnu")
# AHT(227, 30, 15, "simmnu")
# AHT(64, 20, 10, "simmnu")
# AHT(65, 15, 7.5, "simmnu")
# AHT(66, 50, 25, "simmnu")
# AHT(231, 0, 0, "simmnu")
# AHT(232, 30, 15, "simmnu")
# AHT(233, 60, 30, "simmnu")
# AHT(145, 0.75, 0.5, "simmnu")
# AHT(235, 30, 15, "simmnu")
# AHT(236, 30, 15, "simmnu")
# AHT(237, 30, 15, "simmnu")
# AHT(238, 30, 15, "simmnu")
# AHT(239, 30, 15, "simmnu")
# AHT(240, 40, 20, "simmnu")
# AHT(241, 40, 20, "simmnu")
# AHT(242, 30, 15, "simmnu")
# AHT(243, 30, 0, "simmnu")
# AHT(244, 15, 10, "simmnu")
# AHT(245, 15, 10, "simmnu")
# AHT(246, 40, 20, "simmnu")
# AHT(247, 15, 10, "simmnu")
# AHT(248, 15, 10, "simmnu")
# AHT(249, 30, 15, "simmnu")
# AHT(250, 45, 22.5, "simmnu")
# AHT(251, 30, 15, "simmnu")
# AHT(252, 90, 45, "simmnu")
# AHT(253, 45, 22.5, "simmnu")
# AHT(254, 30, 15, "simmnu")
# AHT(255, 30, 15, "simmnu")
# AHT(256, 30, 15, "simmnu")
# AHT(257, 30, 15, "simmnu")
# AHT(258, 30, 15, "simmnu")
# AHT(259, 30, 15, "simmnu")
# AHT(260, 30, 15, "simmnu")
# AHT(261, 30, 15, "simmnu")
# AHT(262, 30, 15, "simmnu")
# AHT(263, 30, 15, "simmnu")
# AHT(264, 30, 15, "simmnu")
# AHT(145, 0.75, 0.5, "simmnu")
# AHT(266, 60, 30, "simmnu")
# AHT(267, 20, 10, "simmnu")
# AHT(268, 120, 60, "simmnu")
# AHT(269, 120, 60, "simmnu")
# AHT(270, 30, 15, "simmnu")
# AHT(271, 120, 60, "simmnu")
# AHT(85, 60, 30, "simmnu")
# AHT(273, 40, 20, "simmnu")
# AHT(274, 30, 15, "simmnu")
# AHT(275, 120, 60, "simmnu")
# AHT(276, 20, 10, "simmnu")
# AHT(277, 20, 10, "simmnu")
# AHT(278, 60, 30, "simmnu")
# AHT(279, 30, 15, "simmnu")
# AHT(280, 30, 15, "simmnu")
# AHT(281, 25, 12.5, "simmnu")
# AHT(203, 10, 5, "simmnu")
# AHT(283, 90, 45, "simmnu")
# AHT(49, 200, 100, "simmnu")
# AHT(34, 30, 15, "simmnu")
# AHT(51, 150, 75, "simmnu")
# AHT(2, 20, 10, "simmnu")
# AHT(74, 50, 25, "simmnu")
# AHT(53, 20, 20, "simmnu")
# AHT(54, 60, 30, "simmnu")
# AHT(55, 120, 60, "simmnu")
# AHT(56, 0, 0, "simmnu")
# AHT(57, 60, 30, "simmnu")
# AHT(58, 150, 75, "simmnu")
# AHT(295, 30, 15, "simmnu")
# AHT(1, 120, 60, "simmnu")
# AHT(145, 0.75, 0.5, "simmnu")
# AHT(298, 150, 75, "simmnu")
# AHT(59, 50, 25, "simmnu")
# AHT(60, 100, 50, "simmnu")
# AHT(61, 15, 7.5, "simmnu")
# AHT(236, 30, 15, "simmnu")
# AHT(237, 30, 15, "simmnu")
# AHT(238, 30, 15, "simmnu")
# AHT(305, 0.5, 0, "simmnu")
# AHT(306, 4.5, 0, "simmnu")
# AHT(307, 2.24, 0, "simmnu")
# AHT(308, 15, 0, "simmnu")
# AHT(63, 30, 10, "simmnu")
# AHT(64, 20, 10, "simmnu")
# AHT(65, 15, 5, "simmnu")
# AHT(66, 50, 25, "simmnu")
# AHT(67, 180, 90, "simmnu")
# AHT(68, 60, 30, "simmnu")
# AHT(69, 300, 150, "simmnu")
# AHT(70, 5, 0, "simmnu")
# AHT(71, 60, 30, "simmnu")
# AHT(72, 300, 150, "simmnu")
# AHT(74, 50, 25, "simmnu")
# AHT(320, 30, 0, "simmnu")
# AHT(321, 30, 0, "simmnu")
# AHT(322, 30, 0, "simmnu")
# AHT(323, 30, 15, "simmnu")
# AHT(324, 30, 15, "simmnu")
# AHT(325, 30, 15, "simmnu")
# AHT(326, 30, 15, "simmnu")
# AHT(327, 30, 15, "simmnu")
#
# NPCategory("US_NA_Deals", "simmnu")
# AHT(1, 20, 10, "simmnu")
# ? Testing
