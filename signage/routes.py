import re
import os
import secrets
import pytz
from PIL import Image
import datetime
import time
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from werkzeug.utils import secure_filename
from signage import app, db, bcrypt
from signage.forms import UserRegistrationForm, UserUpdateForm, LoginForm, AddBranchGroupForm, UpdateBranchGroupForm, AddBranchForm, UpdateBranchForm, AddNewsForm, UpdateNewsForm, AddNodeForm, UpdateNodeForm, AddMediaForm, UpdateMediaForm, AddPlaylistForm, UpdatePlaylistForm, UpdateSettings, AddAddhocForm, AddTemplateForm, AddTemplateItemForm
from signage.models import User, branchGroup, Branch, News, Node, Playlist, Settings, Media, PlaylistMedia, PlaylistDefault, PlaylistAddhoc, NodeStatus, Post, Role, Permission
from flask_login import login_user, current_user, logout_user, login_required


posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog  Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

branch_group = [
    {
        'name': 'Group 1',
        'status': '1',
        'date' : '28/02/2019'    
    },
    {
        'name': 'Group 2',
        'status': '0',
        'date' : '26/02/2019'    
    }
]



branch_list = [
    {
        'group':'Group 1',
        'name': 'Head Office',
        'status': '1',
        'date' : '28/02/2019'    
    },
    {
        'group':'Group 2',
        'name': 'Colombo 2',
        'status': '0',
        'date' : '26/02/2019'    
    }
]


node_list = [
    {
        'group':'Group 1',
        'branch': 'Head Office',
        'name': 'node 1',
        'status': '1',
        'date' : '28/02/2019'    
    },
    {
        'group':'Group 2',
        'branch': 'Colombo2',
        'name': 'node 2',
        'status': '0',
        'date' : '26/02/2019'    
    }
]




setttings_list = [
    {
        'name':'Download Stop (24hours) [00:00:00 = disable]',
        'val':'23:00:00'     
    },    
        {
        'name':'Default Node Download Time (24hours)',
        'val':'03:00:00'     
    },
        {
        'name':'Default Image Duration (Seconds)',
        'val':'15'     
    },
        {
        'name':'File Size Limit (MB)',
        'val':'1024'     
    },
        {
        'name':'Version',
        'val':'0.1'     
    }
    

]

status = [ 
    {
        'group':'group 1',
        'branch':'branch 1',
        'node':'test1',
        'date':'2010-09-10'


    },
        {
        'group':'group 2',
        'branch':'branch 2',
        'node':'test2',
        'date':'2012-02-12'

    },
        {
        'group':'group 3',
        'branch':'branch 3',
        'node':'test3',
        'date':'2018-08-18'

    },
]

user_list = [
    {
    'firstname': 'Test First Name',
    'username':'Test User 1',
    'status': '0',
    'date':'2018-08-18',
    },
   {
    'firstname': 'Second Test First Name',
    'username':'Test User 2',
    'status': '1',
    'date':'2018-08-18',
    }
]

media_list = [
    {
    'media': 'Image',
    'name':'Media Name one',
    'type': 'video',
    'size':'12MB',
    'duration':'00:00:30',
    'status': '1',
    'in_a_playlist':'1',
    'date':'2018-08-18',

    },
   {
    'media': 'Image',
    'name':'Media Name two',
    'type': 'Image',
    'size':'1MB',
    'duration':'00:00:15',
    'status': '0',
    'in_a_playlist':'1',
    'date':'2018-08-26',
   },
      {
    'media': 'Image',
    'name':'Media Name three',
    'type': 'Image',
    'size':'13MB',
    'duration':'00:00:15',
    'status': '1',
    'in_a_playlist':'0',
    'date':'2018-08-26',
   }
]

play_list = [
    {
    'name':'Playlist one',
    'type': 'Full Ad',
    'duration':'00:00:30',
    'status': '1',
    'in_a_schedule':'1',
    'in_a_default_schedule':'1',
    'date':'2018-08-18',

    },
   {
    'name':'Playlist two',
    'type': 'Full Ad',
    'duration':'00:00:30',
    'status': '0',
    'in_a_schedule':'0',
    'in_a_default_schedule':'1',
    'date':'2018-08-18',
   },
      {
    'name':'Playlist three',
    'type': 'Full Ad',
    'duration':'00:00:30',
    'status': '1',
    'in_a_schedule':'0',
    'in_a_default_schedule':'1',
    'date':'2018-08-18',
   }
]


def has_permission(permission_name):
    # Check if the current user has the specified permission
    if current_user.role:
        # for permission in current_user.role.permissions:
        #     print(permission.name)
        #     print(permission_name)
        return any(permission.name == permission_name for permission in current_user.role.permissions)
    return False


@app.route("/")
@app.route("/home")
@login_required
def home():
    status = NodeStatus.query.order_by(NodeStatus.id.desc()).all()
    today = datetime.datetime.now().date()
    ad_sc = PlaylistAddhoc.query.all()
    ad_hc_schedule = []

    for schedule in ad_sc:
        if schedule.start_date.date() <= today <= schedule.end_date.date():
            ad_hc_schedule.append(schedule)
    #        print(schedule.nodes.count())
    return render_template('home.html', posts=posts, status=status, title='Home', ad_hc_schedule=ad_hc_schedule)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/user")
@login_required
def user():

    # Check if the current user has the right role to add users
    if not has_permission('manage_users'):
        abort(403)
    user_list = User.query.order_by(User.id.desc()).all()
    return render_template('user.html', title='User ', users=user_list)  


@app.route("/user/add", methods=['GET', 'POST'])
@login_required
def addUser():
    # Check if the current user has the right role to add users
    if not has_permission('manage_users'):
        abort(403)

    form = UserRegistrationForm()
    roles = Role.query.all()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Fetch the role from the form
        role = Role.query.filter_by(id=form.role_id.data).first()

        user = User(firstname=form.firstname.data, 
                    username=form.username.data, 
                    email=form.email.data, 
                    password=hashed_password, 
                    active_status=form.active_status.data,
                    role_id = role.id
                    )
        db.session.add(user)
        db.session.commit()
        flash(f'User created for {form.username.data} !', 'success')
        return redirect(url_for('user'))
    return render_template('addUser.html', title='User', form=form, hide_pw=False, legend = 'Add User' , roles = roles)


@app.route("/user/<int:user_id>")
@login_required
def viewUser(user_id):
    user = User.query.get_or_404(user_id)
    roles = [x.name for x in current_user.role.permissions]
    return render_template('user_view.html', title='User View', user=user, r=roles)  


@app.route("/user/<int:user_id>/update", methods=['GET', 'POST'])
@login_required
def updateUser(user_id):
    user = User.query.get_or_404(user_id)
    if not has_permission('manage_users'):
        abort(403)

    form = UserUpdateForm()
    if form.validate_on_submit():
        user.firstname=form.firstname.data 
        user.email=form.email.data
        user.active_status=form.active_status.data
        
        # user.role_id=form.role_id.data
        db.session.commit()
        flash(f'User account has been updated !','success')
        return redirect(url_for('user', user_id=user.id))

    elif request.method == 'GET':
         form.firstname.data = user.firstname
         form.email.data = user.email
         form.active_status.data = user.active_status
        #  form.role_id.data = user.role_id

    roles = [x.name for x in current_user.role.permissions]

    return render_template('addUser.html', title='User Update',  form=form, hide_pw=True, legend = 'Update User' , r=roles)  


@app.route("/user/<int:user_id>/delete", methods=['POST'])
@login_required
def deleteUser(user_id):
    user = User.query.get_or_404(user_id)
    if not has_permission('manage_users'):
        abort(403)

    if not (user.id == current_user.id):
        db.session.delete(user)
        db.session.commit()
        flash(f'User account has been deleted !','success')
        return redirect(url_for('user'))
    else:
        flash(f'You Cannot delete your logged accout !','danger')
        return redirect(url_for('user'))



#Fake Login
@app.route("/login", methods=['GET', 'POST'])
def Flogin():
    form = LoginForm()
    if form.validate_on_submit():
            return redirect(url_for('Flogin'))
        
    return render_template('login.html', title='Login',form=form)

#Real Login
@app.route("/Admin/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.active_status:
                login_user(user)
                flash(f'You have been logged in !', 'success')
                return redirect(url_for('home'))
            else:
                flash(f'Login Unsuccessful. Your Account is Deactivated !', 'danger')
        else:
            flash(f'Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='User', form=form)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))




##############SETTINGS############################
@app.route("/settings")
@login_required
def settings():
    #settings = Settings.query.first()
    host_url = request.host_url
    
    settings = Settings.query.first()
    print(settings)

    return render_template('settings.html', title='Settings', sets=settings,host=host_url)




@app.route("/settings/update", methods=['GET', 'POST'])
@login_required
def updateSettings():
    settings = Settings.query.first()
    if not has_permission('manage_settings'):
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdateSettings()
    if form.validate_on_submit():
        download_stop = form.download_stop.data
        download_start = form.download_start.data
        if len(download_stop.split(':')) == 2:
            download_stop += ':00'

        if len(download_start.split(':')) == 2:
            download_start += ':00'

        settings.download_stop = download_stop
        settings.download_start= download_start 
        settings.image_duration=form.image_duration.data
        settings.file_size_limit=form.file_size_limit.data
        settings.time_zone = form.time_zone.data
        settings.file_size_limit_total = form.file_size_limit_total.data
        db.session.commit()
        flash(f'Settings has been updated !','success')
        return redirect(url_for('settings'))

    elif request.method == 'GET':
         form.download_stop.data = settings.download_stop
         form.download_start.data = settings.download_start
         form.image_duration.data = settings.image_duration
         form.file_size_limit.data = settings.file_size_limit
         form.file_size_limit_total.data = settings.file_size_limit_total
         form.time_zone.data = settings.time_zone

    return render_template('settings_update.html', title='Settings Update', pytz_data = pytz.all_timezones,  form=form)  


###############END SETTINGS#######################
       


###############END SETTINGS#######################



@app.route("/actions")
@login_required
def actions():
    if not has_permission('manage_configuration'):
        abort(403)

    branch_group = branchGroup.query.filter_by(active_status=True)
    return render_template('actions.html', title='Actions', groups=branch_group)   






@app.route("/actions/update", methods=['POST'])
@login_required
def actionUpdate():
    if not has_permission('manage_configuration'):
        abort(403)
    nodes = Node.query.filter_by(active_status=True)
    if request.form['submit_button'] == 'Device Restart':
        for br in nodes:
            if request.form.get(br.node_name):
                print(br.node_name)
                ####################
                node_status = NodeStatus.query.filter_by(node_id=br.id).first()
                node_status.device_restart = 1
                db.session.commit()


        flash(f'selected nodes will be restarted within 5 min !', 'success')
        return redirect(url_for('home'))  

    elif request.form['submit_button'] == 'Application Restart':
        for br in nodes:
                if request.form.get(br.node_name):
                    print(br.node_name)
                    #######################
                    node_status = NodeStatus.query.filter_by(node_id=br.id).first()
                    node_status.application_restart = 1
                    db.session.commit()


        flash(f'selected nodes will be updated within 5 min !', 'success')
        return redirect(url_for('home'))  

    else:
        pass 




    flash(f'Invalid Request!', 'danger')
    return redirect(url_for('home'))  



############# BRANCH GROUP ##################

@app.route("/branch/group")
@login_required
def branch_group_function():
    branch_group = branchGroup.query.order_by(branchGroup.id.desc()).all()
    return render_template('branch_group.html', title='Branch Group', branchG=branch_group)  


@app.route("/branch/group/add", methods=['GET', 'POST'])
@login_required
def branch_group_function_Add():
    if not has_permission('manage_configuration'):
        abort(403)
    form = AddBranchGroupForm()
    if form.validate_on_submit():
        branch = branchGroup(
                    branch_group_name=form.branch_group_name.data, 
                    description=form.description.data, 
                    active_status=form.active_status.data,                    
                    )
        db.session.add(branch)
        db.session.commit()

        flash(f'Group {form.branch_group_name.data} Added !', 'success')
        return redirect(url_for('branch_group_function'))

    return render_template('branch_group_add.html', title='Add Branch Group', form=form, legend = 'Add Branch Group ')  

@app.route("/branch/group/<int:branchgroup_id>")
@login_required
def branchGroupView(branchgroup_id):
    branch_group = branchGroup.query.get_or_404(branchgroup_id)
    return render_template('branch_group_view.html', title='Branch View', bGG=branch_group)  



@app.route("/branch/group/<int:branchgroup_id>/update", methods=['GET', 'POST'])
@login_required
def updateBranchGroup(branchgroup_id):
    branch_group = branchGroup.query.get_or_404(branchgroup_id)
    if not current_user.manage_configuration == 1:
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdateBranchGroupForm()
    if form.validate_on_submit():
        fval = form.branch_group_name.data
        print(fval)
        f_user = branchGroup.query.filter_by(branch_group_name=fval).first()

        if f_user:
            if (branchgroup_id != f_user.id):
                flash(f'You cannot duplicate branch group name !','danger')
                return redirect(url_for('branch_group_function'))

        branch_group.branch_group_name=form.branch_group_name.data 
        branch_group.description=form.description.data
        branch_group.active_status=form.active_status.data
        db.session.commit()
        flash(f'Branch Group has been updated !','success')
        return redirect(url_for('branchGroupView', branchgroup_id=branchgroup_id))

    elif request.method == 'GET':
         form.branch_group_name.data = branch_group.branch_group_name
         form.description.data = branch_group.description
         form.active_status.data = branch_group.active_status
       

    return render_template('branch_group_add.html', title='Branch Update',  form=form, legend = 'Update Branch Group')  



@app.route("/branch/group/<int:branchgroup_id>/delete", methods=['POST'])
@login_required
def deleteBranchGroup(branchgroup_id):
    branch_group = branchGroup.query.get_or_404(branchgroup_id)
    if not current_user.manage_configuration == 1:
        abort(403)

    db.session.delete(branch_group)
    try:
        db.session.commit()
        flash(f'Branch Group has been deleted !','success')
        return redirect(url_for('branch_group_function'))
    except:
        flash(f'Branch Group has Branches !','danger')
        return redirect(url_for('branch_group_function'))


############# Branch Group End ###################



############ Branch #########################
@app.route("/branch")
@login_required
def branch():
    branch_list =  Branch.query.order_by(Branch.id.desc()).all()
    return render_template('branch.html', title='Branch', branch=branch_list)  



@app.route("/branch/add", methods=['GET', 'POST'])
@login_required
def branch_Add():
    if not has_permission('manage_configuration'):
        abort(403)

    branch_group = branchGroup.query.filter_by(active_status=True)
    form = AddBranchForm()
    if form.validate_on_submit():
        branch = Branch(
                    branch_group_id=form.branch_group_id.data, 
                    branch_name=form.branch_name.data, 
                    description=form.description.data,
                    active_status=form.active_status.data,                    
                    )
        db.session.add(branch)
        db.session.commit()


        flash(f'Branch {form.branch_name.data} Added !', 'success')
        return redirect(url_for('branch'))

    return render_template('branch_add.html', title='Add Branch', form=form, groups=branch_group, legend="Add Branch")  


@app.route("/branch/<int:branch_id>")
@login_required
def branchView(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    return render_template('branch_view.html', title='Branch View', bGG=branch, branch=True)  


@app.route("/branch/<int:branch_id>/update", methods=['GET', 'POST'])
@login_required
def updateBranch(branch_id):
    branch_group = branchGroup.query.filter_by(active_status=True)
    branch = Branch.query.get_or_404(branch_id)
    if not current_user.manage_configuration == 1:
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdateBranchForm()
    if form.validate_on_submit():
        fval = form.branch_name.data
        gfval = form.branch_group_id.data
        print(fval)
        f_user = Branch.query.filter_by(branch_name=fval, branch_group_id=gfval).first()

        if f_user:
            if (branch_id != f_user.id):
                flash(f'You cannot duplicate !','danger')
                return redirect(url_for('branch'))

        branch.branch_group_id = form.branch_group_id.data
        branch.branch_name=form.branch_name.data 
        branch.description=form.description.data
        branch.active_status=form.active_status.data
        db.session.commit()
        flash(f'Branch has been updated !','success')
        return redirect(url_for('branchView', branch_id=branch_id))

    elif request.method == 'GET':
         print(branch.branch_group_id)
         selected = branch.branch_group_id
         form.branch_name.data = branch.branch_name
         form.description.data = branch.description
         form.active_status.data = branch.active_status
       

    return render_template('branch_add.html', title='Branch Update',  form=form, groups=branch_group, legend = 'Update Branch Group', selected=selected)  


@app.route("/branch/<int:branch_id>/delete", methods=['POST'])
@login_required
def deleteBranch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    if not has_permission('manage_configuration'):
        abort(403)
    try:
        db.session.delete(branch)
        db.session.commit()
        flash(f'Branch has been deleted !','success')
        return redirect(url_for('branch'))
    except:
        flash(f'Branch has Nodes !','danger')
        return redirect(url_for('branch'))

###########################NODE##########################################

@app.route("/node")
@login_required
def node():
    node_list =  Node.query.order_by(Node.id.desc()).all()
    return render_template('node.html', title='Node', nodes=node_list)  


@app.route("/node/add", methods=['GET', 'POST'])
@login_required
def node_Add():

    if not has_permission('manage_configuration'):
        abort(403)

    branch_group = branchGroup.query.filter_by(active_status=True)
    form = AddNodeForm()
    print(form)
    if form.validate_on_submit():

        node = Node(
                    branch_id=form.branch_id.data, 
                    node_name=form.node_name.data,
                    node_password=form.node_password.data, 
                    description=form.description.data,
                    active_status=form.active_status.data,                    
                    )
        db.session.add(node)
        db.session.commit()

        node_id = db.session.query(Node).order_by(Node.id.desc()).first()

        node_status = NodeStatus(
                node_id=node_id.id
                )
        db.session.add(node_status)
        db.session.commit()

        flash(f'Node {form.node_name.data} Added !', 'success')
        return redirect(url_for('node'))
    else:
        print("Error")

    return render_template('node_add.html', title='Add Node', form=form, groups=branch_group, legend='Add Node')  



@app.route("/node/getdata", methods=['POST'])
def get_branches_for_group():

    group_id=request.form['group_id']
    branches = Branch.query.filter_by(active_status=True,branch_group_id=group_id)
    ret = ''
    for x in branches:
        ret +=  '<option value="%i">%s</option>' % (x.id, x.branch_name)

    print(branches.count())
    if branches.count() == 0:
        ret = '<option value="" disable> No branches in this group</option>'
    return ret


@app.route("/node/<int:node_id>")
@login_required
def nodeView(node_id):
    node = Node.query.get_or_404(node_id)
    return render_template('node_view.html', title='Node View', bGG=node)  




@app.route("/node/<int:node_id>/update", methods=['GET', 'POST'])
@login_required
def updateNode(node_id):
    branch_group = branchGroup.query.filter_by(active_status=True)
    node = Node.query.get_or_404(node_id)
    if not has_permission('manage_configuration'):
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdateNodeForm()
    if form.validate_on_submit():
        fval = form.node_name.data
        print(fval)
        f_node = Node.query.filter_by(node_name=fval).first()

        if f_node:
            if (node_id != f_node.id):
                flash(f'You cannot duplicate !','danger')
                return redirect(url_for('node'))

        node.branch_id = form.branch_id.data
        node.node_name=form.node_name.data 
        node.node_password=form.node_password.data 
        node.description=form.description.data
        node.active_status=form.active_status.data
        db.session.commit()
        flash(f'Node has been updated !','success')
        return redirect(url_for('nodeView', node_id=node_id))

    elif request.method == 'GET':
#         print(branch.branch_group_id)
         selected = node.branch.group.id
         form.branch_group_id.data = node.branch.group
         form.branch_id.data = node.branch_id
         branch_val = node.branch
         form.node_name.data = node.node_name
         form.node_password.data = node.node_password
         password_val = node.node_password
         form.description.data = node.description
         form.active_status.data = node.active_status


    return render_template('node_add.html', title='Node Update', branch_val=branch_val, password_val=password_val, form=form, groups=branch_group, legend = 'Update Node', selected=selected)  




@app.route("/node/<int:node_id>/delete", methods=['POST'])
@login_required
def deleteNode(node_id):
    node = Node.query.get_or_404(node_id)
    if not has_permission('manage_configuration'):
        abort(403)

    db.session.delete(node)
    db.session.commit()
    flash(f'Node has been deleted !','success')
    return redirect(url_for('node'))


#############################END NODE######################################



###############################MEDIA######################################
@app.route("/media")
@login_required
def media():
    media_list = Media.query.order_by(Media.id.desc()).all()
    return render_template('media.html', title='Media', media=media_list)  


def save_media(form_media,media_name):
    _, f_ext = os.path.splitext(form_media.filename)
    media_fn = media_name + f_ext
    media_path = os.path.join(app.root_path, 'static/upload_assets/upload_media', media_fn)
    form_media.save(media_path)
    return media_fn


def save_thumb(form_media):
    sec_name = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_media.filename)
    if f_ext == '.mp4':
        media_fn = 'default.png'
        return media_fn

    media_fn = sec_name + f_ext
    media_path = os.path.join(app.root_path, 'static/upload_assets/upload_media/thumbnails', media_fn)
    output_size = (80,60)
    i = Image.open(form_media)
    i.thumbnail(output_size)
    i.save(media_path)
    return media_fn


# @app.route("/media/add", methods=['GET', 'POST'])
# @login_required
# def media_Add():
#     if not has_permission('manage_content'):
#         abort(403)

#     form = AddMediaForm()
#     if form.validate_on_submit():
#         if not re.match("^[A-Za-z0-9_-]*$", form.media_name.data):
#             return redirect(url_for('media_Add'))

#         media_file = save_media(form.media_file.data, form.media_name.data)
#         thumb_file = save_thumb(form.media_file.data)

#         print("MEDIA Saved")
#         b = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upload_assets/upload_media/'+media_file)
#         c = os.path.getsize(b)
#         kb = str(round(c/(1000*1000),2)) + ' MB'
#         print("MEDIA Saved")

#         if media_file.split('.')[1] == 'mp4':
#             m_format = 'Video'
#             duration =  '0'+str(datetime.timedelta(seconds=int(form.media_duration.data.split('.')[0])))
#         else:
#             m_format = 'Image'
#             duration = '00:00:' + str(Settings.query.get_or_404(1).image_duration)

#         print("fine")
#         media = Media(
#                     media_name=media_file,
#                     media_thumb_name = thumb_file,
#                     media_file_size = kb,
#                     media_type = m_format,
#                     media_duration = duration,
#                     description=form.description.data,
#                     active_status=form.active_status.data,                    
#                     )
#         print(media)
#         db.session.add(media)
#         db.session.commit()


#         flash(f'Media {form.media_name.data} Added !', 'success')
#         #return redirect(url_for('media'))
#         return jsonify({'Valid':'True'})



#     return render_template('media_add.html', title='Add Media', legend = 'Add Media', form=form, update=False)  
@app.route("/media/add", methods=['GET', 'POST'])
@login_required
def media_Add():
    if not has_permission('manage_content'):
        abort(403)

    form = AddMediaForm()
    settings = Settings.query.get_or_404(1)

    if form.validate_on_submit():
        # --- Media name validation ---
        if not re.match("^[A-Za-z0-9_-]*$", form.media_name.data):
            return jsonify({
                'Valid': False,
                'error': "Media name contains invalid characters (only letters, numbers, _ and - allowed)."
            })

        # --- Check uploaded file size ---
        uploaded_file = form.media_file.data
        uploaded_file.seek(0, os.SEEK_END)
        file_size_bytes = uploaded_file.tell()
        uploaded_file.seek(0)  # reset pointer
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

        if file_size_mb > settings.file_size_limit:
            return jsonify({
                'Valid': False,
                'error': f"File too large! Limit is {settings.file_size_limit} MB"
            })

        # --- Check total size of all media ---
        total_size_strs = db.session.query(Media.media_file_size).all()  # values like "12.3 MB"
        total_size_mb = sum(float(s[0].replace(" MB", "")) for s in total_size_strs)

        if (total_size_mb + file_size_mb) > settings.file_size_limit_total:
            return jsonify({
                'Valid': False,
                'error': f"Total media size limit exceeded! "
                         f"Limit = {settings.file_size_limit_total} MB"
            })

        # --- Save media only after checks pass ---
        media_file = save_media(uploaded_file, form.media_name.data)
        thumb_file = save_thumb(uploaded_file)

        if media_file.split('.')[-1].lower() == 'mp4':
            m_format = 'Video'
            duration = '0' + str(datetime.timedelta(
                seconds=int(float(form.media_duration.data.split('.')[0])))
            )
        else:
            m_format = 'Image'
            duration = f"00:00:{settings.image_duration}"

        media = Media(
            media_name=media_file,
            media_thumb_name=thumb_file,
            media_file_size=f"{file_size_mb} MB",
            media_type=m_format,
            media_duration=duration,
            description=form.description.data,
            active_status=form.active_status.data,
        )

        db.session.add(media)
        db.session.commit()

        return jsonify({'Valid': True})

    # If GET or invalid form
    return render_template(
        'media_add.html',
        title='Add Media',
        legend='Add Media',
        form=form,
        update=False
    )




@app.route("/media/<int:media_id>/view", methods=['GET', 'POST'])
@login_required
def viewMedia(media_id):
    media = Media.query.get_or_404(media_id)

    return render_template('media_view.html', title='View Media', media=media)  



@app.route("/media/<int:media_id>/update", methods=['GET', 'POST'])
@login_required
def updateMedia(media_id):
    ###change related playlist duration and site
    playlist_list = []
    plm = PlaylistMedia.query.filter_by(media_id=media_id).all()
    for x in plm:
        playlist_list.append(x.playlist_id)
    ############################################


    media = Media.query.get_or_404(media_id)
    if not has_permission('manage_content'):
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdateMediaForm()
    if form.validate_on_submit():
        media.description=form.description.data
        media.active_status=form.active_status.data
        db.session.commit()
        ###change related playlist duration and site
        for playlist_id in playlist_list:
            try:

                playlist = Playlist.query.get_or_404(playlist_id)

                #plmedia = PlaylistMedia.query.filter_by(playlist_id=playlist_id)
                plmedia = PlaylistMedia.query.filter_by(playlist_id=playlist_id).join(PlaylistMedia.media).filter_by(active_status=1)
                plmedia_duration = PlaylistMedia.query.filter_by(playlist_id=playlist_id).join(PlaylistMedia.media).filter_by(active_status=1)
                time_list = []
                size_list = []


                totalSize = 0.0
                totalSecs = 0

                for x in plmedia_duration:
                    time_list.append(x.duration)

                for x in plmedia: 
                    size_list.append(x.media.media_file_size)

                for tm in time_list:
                    timeParts = [int(s) for s in tm.split(':')]
                    totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
                totalSecs, sec = divmod(totalSecs, 60)
                hr, min = divmod(totalSecs, 60)
                total_time = "%02d:%02d:%02d" % (hr, min, sec)

                for s in size_list:
                    s=float(s.split(' ')[0])
                    totalSize += s


                ###update new value to database
                playlist.total_duration = total_time
                playlist.total_size = round(totalSize,2)
                playlist.total_items = plmedia.count()
                db.session.commit()

            except:
                pass
###########################


        flash(f'Media has been updated !','success')
        return redirect(url_for('media'))

    elif request.method == 'GET':
         form.media_name.data = media.media_name
         form.description.data = media.description
         form.active_status.data = media.active_status


    return render_template('media_add.html', title='Media Update',form=form, legend = 'Update Media', update=True)  




@app.route("/media/<int:media_id>/delete", methods=['POST'])
@login_required
def deleteMedia(media_id):
    ###change related playlist duration and site
    playlist_list = []
    plm = PlaylistMedia.query.filter_by(media_id=media_id).all()
    for x in plm:
        playlist_list.append(x.playlist_id)
    ############################################

    media = Media.query.get_or_404(media_id)
    # if not current_user.manage_content == 1:
    #     abort(403)

    if not has_permission('manage_content'):
        abort(403)

    db.session.delete(media)
    try:
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upload_assets/upload_media/'+media.media_name))
        os.remove(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/upload_assets/upload_media/thumbnails/'+media.media_thumb_name))
    except:
        pass
    db.session.commit()

############################
###change related playlist duration and site
    for playlist_id in playlist_list:
        try:

            playlist = Playlist.query.get_or_404(playlist_id)

            #plmedia = PlaylistMedia.query.filter_by(playlist_id=playlist_id)
            plmedia = PlaylistMedia.query.filter_by(playlist_id=playlist_id).join(PlaylistMedia.media).filter_by(active_status=1)
            plmedia_duration = PlaylistMedia.query.filter_by(playlist_id=playlist_id)
            time_list = []
            size_list = []


            totalSize = 0.0
            totalSecs = 0

            for x in plmedia_duration:
                time_list.append(x.duration)

            for x in plmedia: 
                size_list.append(x.media.media_file_size)

            for tm in time_list:
                timeParts = [int(s) for s in tm.split(':')]
                totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
            totalSecs, sec = divmod(totalSecs, 60)
            hr, min = divmod(totalSecs, 60)
            total_time = "%02d:%02d:%02d" % (hr, min, sec)

            for s in size_list:
                s=float(s.split(' ')[0])
                totalSize += s


            ###update new value to database
            playlist.total_duration = total_time
            playlist.total_size = round(totalSize,2)
            playlist.total_items = plmedia.count()
            db.session.commit()

        except:
            pass
###########################



    flash(f'Media has been deleted !','success')
    return redirect(url_for('media'))



#############################END MEDIA####################################
#######################PLAYLIAST####################
@app.route("/playlist")
@login_required
def playlist():
    play_list = Playlist.query.order_by(Playlist.id.desc()).all()
    return render_template('playlist.html', title='Playlist ', play_list=play_list)  




@app.route("/playlist/<int:pl_id>/preview", methods=['GET'])
@login_required
def previewsPlaylist(pl_id):
    playlist = Playlist.query.get_or_404(pl_id)
    if not has_permission('manage_content'):
        abort(403)

    plmedia = PlaylistMedia.query.filter_by(playlist_id=pl_id).join(PlaylistMedia.media).filter_by(active_status=1)

    


    return render_template('playlist_preview.html', playlist=playlist, plmedia = plmedia, title='Plalist Preview', legend = 'Plalist Preview')  



@app.route("/media/playlist/preview", methods=['POST'])
def get_media_for_playlist_preview():

    media_id=request.form['media_id']
    media = Media.query.get_or_404(media_id)
    ret = ''
    if media.media_type == 'Video':
         ret = 'Video=/static/upload_assets/upload_media/'+media.media_name
    else:        
         ret = 'Image=/static/upload_assets/upload_media/'+media.media_name
    print(ret)
    #ret = ''
    # for x in branches:
    #     ret +=  '<option value="%i">%s</option>' % (x.id, x.branch_name)

    # print(branches.count())
    # if branches.count() == 0:
    #     ret = '<option value="" disable> No branches in this group</option>'
    return ret





@app.route("/playlist/add", methods=['GET', 'POST'])
@login_required
def playlist_Add():
    if not has_permission('manage_content'):
        abort(403)

    form = AddPlaylistForm()
    if form.validate_on_submit():
        playlist = Playlist(
                    playlist_name=form.playlist_name.data, 
                    description=form.description.data,
                    active_status=form.active_status.data,                    
                    )
        db.session.add(playlist)
        db.session.commit()

        
        flash(f'Playlist {form.playlist_name.data} Added !', 'success')
        return redirect(url_for('playlist'))

    return render_template('playlist_add.html', title='Add Playlist', form=form, legend='Add Playlist')  



@app.route("/playlist/<int:pl_id>/update", methods=['GET', 'POST'])
@login_required
def updatePlaylist(pl_id):
    playlist = Playlist.query.get_or_404(pl_id)
    if not has_permission('manage_content'):
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdatePlaylistForm()
    if form.validate_on_submit():
        fval = form.playlist_name.data
        print(fval)
        f_playlist = Playlist.query.filter_by(playlist_name=fval).first()

        if f_playlist:
            if (pl_id != f_playlist.id):
                flash(f'You cannot duplicate !','danger')
                return redirect(url_for('playlist'))

        playlist.playlist_name=form.playlist_name.data 
        playlist.description=form.description.data
        playlist.active_status=form.active_status.data
        db.session.commit()
        flash(f'Playlist has been updated !','success')
        return redirect(url_for('playlist'))

    elif request.method == 'GET':
         form.playlist_name.data = playlist.playlist_name
         form.playlist_type.data = playlist.playlist_type
         form.description.data = playlist.description
         form.active_status.data = playlist.active_status


    return render_template('playlist_add.html', title='Node Update', form=form, legend = 'Update Node')  






@app.route("/playlist/<int:pl_id>/delete", methods=['POST'])
@login_required
def deletePlaylist(pl_id):
    playlist = Playlist.query.get_or_404(pl_id)
    if not has_permission('manage_configuration'):
        abort(403)

    db.session.delete(playlist)
    db.session.commit()

#####################DELETE REFERENCE IN Playlist media, DEFAULT PLAYLISTS and AD-hoc Playlist###############
    df_pl = PlaylistDefault.query.filter_by(playlist_id=pl_id).all()
    for x in df_pl:
        db.session.delete(x)
        db.session.commit()

    ad_pl = PlaylistAddhoc.query.filter_by(playlist_id=pl_id).all()
    for x in ad_pl:
        db.session.delete(x)
        db.session.commit()        


    media_pl = PlaylistMedia.query.filter_by(playlist_id=pl_id).all()
    for x in media_pl:
        db.session.delete(x)
        db.session.commit()  

    flash(f'Playlist has been deleted !','success')
    return redirect(url_for('playlist'))


#######PLAYLIST ADD MEDIA########

@app.route("/playlist/items/<int:playlist_id>")
@login_required
def playlist_items(playlist_id):
    if not has_permission('manage_content'):
        abort(403)


    media_list = Media.query.filter_by(active_status=True).order_by(Media.id.desc())
    playlist = Playlist.query.get_or_404(playlist_id)

    #plmedia = PlaylistMedia.query.filter_by(playlist_id=playlist_id)
    plmedia = PlaylistMedia.query.filter_by(playlist_id=playlist_id).join(PlaylistMedia.media).filter_by(active_status=1)
    plmedia_duration = PlaylistMedia.query.filter_by(playlist_id=playlist_id)
    time_list = []
    size_list = []


    totalSize = 0.0
    totalSecs = 0

    for x in plmedia_duration:
        time_list.append(x.duration)

    for x in plmedia: 
        size_list.append(x.media.media_file_size)

    for tm in time_list:
        timeParts = [int(s) for s in tm.split(':')]
        totalSecs += (timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2]
    totalSecs, sec = divmod(totalSecs, 60)
    hr, min = divmod(totalSecs, 60)
    total_time = "%02d:%02d:%02d" % (hr, min, sec)

    for s in size_list:
        s=float(s.split(' ')[0])
        totalSize += s


    ###update new value to database
    playlist.total_duration = total_time
    playlist.total_size = round(totalSize,2)
    playlist.total_items = plmedia.count()
    db.session.commit()
    #############################
    if plmedia.count() == 0:
        val = False
    else:
        val = True


    return render_template('playlist_items.html', title='Playlist Items', plmedia=plmedia, media=media_list , playlist=playlist,val=val)  


@app.route("/playlist/items/<int:playlist_id>/<int:media_id>/add")
@login_required
def playlist_items_add(playlist_id, media_id):
    if not has_permission('manage_content'):
        abort(403)

    media = Media.query.get_or_404(media_id)
    playlist = Playlist.query.get_or_404(playlist_id)

    plmedia_count = PlaylistMedia.query.filter_by(playlist_id=playlist_id).count()

    if plmedia_count >= 1:
        pass
        ####fix order number duplicate
        pl = PlaylistMedia.query.filter_by(playlist_id=playlist_id).order_by(PlaylistMedia.order.asc()).all()
        plmedia_count = pl[-1].order

    playlist_media = PlaylistMedia(
                playlist_id=playlist_id, 
                media_id=media_id,
                order = plmedia_count+1,
                duration = media.media_duration,                    
                )
    db.session.add(playlist_media)
    db.session.commit()



    return redirect(url_for('playlist_items', playlist_id=playlist.id))



@app.route("/playlist/items/update", methods=['POST'])
def updatePlaylistDuration():

    plmedia_id=request.form['plmedia_id']
    duration=request.form['duration']
    playlist_id=request.form['playlist_id']
    try:
        k = time.strptime(duration, "%H:%M:%S")
    except:
        flash(f'Invalid Input ! (input - 00:00:00)', 'danger')
        return redirect(url_for('playlist_items', playlist_id=playlist_id))    

    
    playlist_media = PlaylistMedia.query.get_or_404(plmedia_id)
    playlist_media.duration = duration
    db.session.commit()
    return redirect(url_for('playlist_items', playlist_id=playlist_id))



@app.route("/playlist/items/<int:playlistmedia_id>/<int:playlist_id>/delete", methods=['POST'])
@login_required
def deletePlaylistItem(playlistmedia_id, playlist_id):
    playlist_items = PlaylistMedia.query.get_or_404(playlistmedia_id)
    if not has_permission('manage_configuration'):
        abort(403)

    db.session.delete(playlist_items)
    db.session.commit()
    return redirect(url_for('playlist_items', playlist_id=playlist_id))

######END PLAYLIST ADD MEDIA####




####################################END PLAYLIST####################################
@app.route("/template")
@login_required
def template():
    return render_template('template.html', title='Template ', template_list=play_list)  


@app.route("/template/add", methods=['GET', 'POST'])
@login_required
def template_Add():
    form = AddTemplateForm()
    if form.validate_on_submit():
        flash(f'Template {form.template_name.data} Added !', 'success')
        return redirect(url_for('template'))

    return render_template('template_add.html', title='Add Template', form=form)  



@app.route("/template/items", methods=['GET', 'POST'])
@login_required
def templates_items():
    form = AddTemplateItemForm()
    if form.validate_on_submit():
        flash(f'Template item Added !', 'success')
        return redirect(url_for('template_items'))
    return render_template('template_items.html', title='Template Items', media=media_list , val=False, form=form)  




@app.route("/news/add", methods=['GET', 'POST'])
@login_required
def newsAdd():
    if not has_permission('manage_news'):
        abort(403)

 #   branch_group = branchGroup.query.filter(branchGroup.branchs.has(Branch.active_status=True))
    branch_group = branchGroup.query.filter_by(active_status=True)
    #branch_group = branchGroup.query.all()
    news_count = News.query.count()

    form = AddNewsForm()
    branch = Branch.query.filter_by(active_status=True)
    #####
    #news order fix
    ####
    if news_count >= 1:
        pass
        ####fix order number duplicate
        pl = db.session.query(News).order_by(News.order).all()
        news_count = pl[-1].order

    if form.validate_on_submit():
        news = News(
                    heading=form.heading.data, 
                    body=form.body.data, 
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    never_expire=form.never_expire.data,  
                    active_status=form.active_status.data,                    
                    order = news_count + 1
                    )
        db.session.add(news)
        db.session.commit()
        if request.method == 'POST':
            for br in branch:
        #        print(form.br.branch_name.data)
        #        print(br.branch_name)
                if request.form.get(br.branch_name):
                    br.news.append(news)
                    db.session.commit()


        flash(f'News  Added !', 'success')
        return redirect(url_for('news'))

#    return render_template('branch_add.html', title='Add Branch', form=form, groups=branch_group, legend="Add Branch")  

    return render_template('news_add.html',order=False, title='Add News', form=form, groups = branch_group, legend="Add News")




@app.route("/news", methods=['GET', 'POST'])
@login_required
def news():
    news = News.query.all()
    return render_template('news.html', title='News', news = news)


@app.route("/news/<int:news_id>")
@login_required
def newsView(news_id):
    news = News.query.get_or_404(news_id)
    return render_template('news_view.html', title='News View', news=news)  


@app.route("/news/<int:news_id>/update", methods=['GET', 'POST'])
@login_required
def updateNews(news_id):
    branch_group = branchGroup.query.filter_by(active_status=True)
    news = News.query.get_or_404(news_id)
    if not has_permission('manage_news'):
        abort(403)
    #branch_group.branch_group_name != 

    form = UpdateNewsForm()
    branch = Branch.query.filter_by(active_status=True)
    if form.validate_on_submit():
        news.heading = form.heading.data
        news.body=form.body.data 
        news.start_date=form.start_date.data
#        news.end_date=form.end_date.data
        news.never_expire=form.never_expire.data
        news.active_status=form.active_status.data
        news.order=form.order.data
        if news.never_expire == 0:
            news.end_date=form.end_date.data

        old_news = news.branches
        news.branches = []
        db.session.commit()

        change = False
        for br in branch:
            if request.form.get(br.branch_name):
                br.news.append(news)
                db.session.commit()
                change = True

        if not change:
            news.branches = old_news
            db.session.commit()

#        if form.active_status.data == 0:
#            news.branches = []
#            db.session.commit()
            




        flash(f'News has been updated !','success')
        return redirect(url_for('newsView', news_id=news_id))

    elif request.method == 'GET':
        selected = news.branches
        form.heading.data = news.heading
        form.body.data = news.body
        form.start_date.data = news.start_date
        form.end_date.data = news.end_date
        form.never_expire.data = news.never_expire
        form.active_status.data = news.active_status
        form.order.data = news.order
        selected_list = []
        selected_grp_list = []
        for dat in selected:
            selected_list.append(dat.id)
            selected_grp_list.append(dat.branch_group_id)


    return render_template('news_add.html', order=True, title='News Update',  form=form, groups=branch_group, legend = 'Update Branch Group', selected=selected_list , selected_grp=selected_grp_list) 




@app.route("/news/<int:news_id>/delete", methods=['POST'])
@login_required
def deleteNews(news_id):
    news = News.query.get_or_404(news_id)
    if not has_permission('manage_news'):
        abort(403)

    db.session.delete(news)
    db.session.commit()
    flash(f'News has been deleted !','success')
    return redirect(url_for('news'))


@app.route("/news/publish", methods=['GET','POST'])
@login_required
def publishNews():
    ## Do news publish
    NodeStatus.query.filter_by().update(dict(news=1))
    db.session.commit()


    flash(f'News has been published !','success')
    return redirect(url_for('news'))  



@app.route("/default/schedule", methods=['GET', 'POST'])
@login_required
def defaultSchedule():
    if not has_permission('manage_schedule'):
        abort(403)
    branch_group = branchGroup.query.filter_by(active_status=True)
    playlist_group = Playlist.query.filter_by(active_status=True).filter(Playlist.total_size != '0.0')

    if request.method == 'POST':
        print('Post request')
        nodes=request.form['nodes'].split(',')
        print(nodes)
        playlist_id=request.form['playlist_id']
        get_p_d = PlaylistDefault.query.filter_by(playlist_id=playlist_id).first()
        if not get_p_d:
            print('NEW Record !!!')
            playlist_default = PlaylistDefault(
                    playlist_id=playlist_id
                )
            db.session.add(playlist_default)
            db.session.commit()

            current_p_d_id = PlaylistDefault.query.filter_by(playlist_id=playlist_id).first().id
        else:
            current_p_d_id = get_p_d.id

        for x in nodes:
            print(x)
            node_data = Node.query.get(int(x))
            node_data.playlist_default_id = current_p_d_id
  
        db.session.commit()
    nodes_data = Node.query.filter_by(active_status=True)

    return render_template('default_schedule.html', title='Default Schedule', groups=branch_group, playlists=playlist_group, nodes=nodes_data)




####################AD HOC SCHEDULE#################################

@app.route("/adhocschedule", methods=['GET', 'POST'])
@login_required
def adhocschedule():
    adhoc = PlaylistAddhoc.query.order_by(PlaylistAddhoc.id.desc()).all()
    return render_template('adhoc.html', title='Ad-Hoc Schedule', adhoc = adhoc)


@app.route("/adhocschedule/<int:schedule_id>", methods=['GET', 'POST'])
@login_required
def adhocschedule_view(schedule_id):
    adhoc = PlaylistAddhoc.query.get_or_404(schedule_id)
    return render_template('adhoc_schedule_view.html', title='Ad-Hoc Schedule View', adhoc = adhoc)



@app.route("/adhocschedule/schedule/add", methods=['GET', 'POST'])
@login_required
def adhocschedule_add():
    if not has_permission('manage_schedule'):
        abort(403)
    branch_group = branchGroup.query.filter_by(active_status=True)
    playlist_group = Playlist.query.filter_by(active_status=True).filter(Playlist.total_size != '0.0')
    node = Node.query.all()
    form = AddAddhocForm()
    if form.validate_on_submit():
        st_date = form.start_date.data
        ed_date = form.end_date.data
        if st_date > ed_date:
            flash(f'Invalid Start Date and End Date !','danger')
            return redirect(url_for('adhocschedule_add')) 

        st_time = form.start_time.data
        ed_time = form.end_time.data
        if(datetime.datetime.strptime(st_time, '%H:%M:%S') > datetime.datetime.strptime(ed_time, '%H:%M:%S')):
            flash(f'Invalid Start Time and End Time !','danger')
            return redirect(url_for('adhocschedule_add')) 

        adhoc_sh = PlaylistAddhoc(
                    addhoc_name=form.addhoc_name.data, 
                    playlist_id=form.playlist_id.data, 
                    start_date=form.start_date.data,
                    end_date=form.end_date.data,
                    start_time=form.start_time.data,  
                    end_time=form.end_time.data,                    
                    description = form.description.data
                    )
        db.session.add(adhoc_sh)
        db.session.commit()

        for n in node:
            if request.form.get(n.node_name):
                print(n.node_name)
                n.adhoc.append(adhoc_sh)
                db.session.commit()

        flash(f'AdHoc Schedules has been added !','success')
        return redirect(url_for('adhocschedule')) 



    return render_template('adhoc_schedule.html', title='Ad-Hoc Schedule',form=form, groups=branch_group, playlists=playlist_group )

@app.route("/adhocschedule/<int:schedule_id>/delete", methods=['POST'])
@login_required
def deleteAdhocSchedule(schedule_id):
    adhoc = PlaylistAddhoc.query.get_or_404(schedule_id)
    if not has_permission('manage_schedule'):
        abort(403)
    adhoc.nodes = []
    db.session.commit()
    db.session.delete(adhoc)
    db.session.commit()
    flash(f'Ad-hoc Schedule has been deleted !','success')
    return redirect(url_for('adhocschedule'))



@app.route("/adhocschedule/publish", methods=['GET','POST'])
@login_required
def publishMediaAdhoc():
    ## Do news publish
    NodeStatus.query.filter_by().update(dict(background_downloading=1))
    db.session.commit()


    flash(f'AdHoc Schedules has been published !','success')
    return redirect(url_for('home')) 


# @app.route("/default/adhocschedule/add", methods=['GET', 'POST'])
# @login_required
# def adhocScheduleAdd():
#     if not current_user.manage_schedule == 1:
#         abort(403)
#     branch_group = branchGroup.query.filter_by(active_status=True)
#     playlist_group = Playlist.query.filter_by(active_status=True).filter(Playlist.total_size != None)

#     if request.method == 'POST':
#         print('Post request')
#         nodes=request.form['nodes'].split(',')
#         playlist_id=request.form['playlist_id']
#     nodes_data = Node.query.filter_by(active_status=True)

#     return render_template('default_schedule.html', title='Default Schedule', groups=branch_group, playlists=playlist_group, nodes=nodes_data)



####################END AD HOC SCHEDULE#################################







#######################################################################
#######################################################################
#######################################################################



###############NODE LOGIN###################################
@app.route('/Service2.svc/login/<username>/<password>')
def nodeLogin(username,password):
    node = Node.query.filter_by(node_name=username, node_password=password, active_status=1).first()
    if node:
        status = str(node.id)
        branch = str(node.branch.branch_name)
    else:
        branch = "-1"
        status = "-1"


    list={"BranchName": branch, "Status": status}
    return jsonify(list)
############################################################

###################GET TEMPLATE SEQUENCE####################
@app.route('/Service2.svc/GetTemplateSequence/<int:number>')
def nodeTemplateSequence(number):
    ### still in develop ###

    list=[{"Duration":"23:00:00","TemplateName":"AdFull"}]
    return jsonify(list)
############################################################

#################DATE TIME##################################
@app.route('/Service2.svc/GetTime/<int:number>')
def nodeDateTime(number):
    dt = str(datetime.datetime.now())
    d_dt = dt.split(' ')[0].replace('-','')
    t_dt = dt.split(' ')[1].split('.')[0].replace(':','')
    full_dt = d_dt+'.'+t_dt

    sett = Settings.query.get(1)
    d_stop = sett.download_stop
    d_start = sett.download_start
    ver = str(sett.version)

    list={"DateTime":str(full_dt),"DownloadStop":str(d_stop),"DownloadTime":str(d_start),"Version":str(ver)}
    return jsonify(list)
###########################################################

#####################GET MEDIA#############################
@app.route('/Service2.svc/GetDownloadMedia/<date>/<int:node>')
def nodeGetMedia(date,node):
    media = [] ### needs to add ad-hoc media
    today = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    try:
        data_node = Node.query.get_or_404(node)
        if data_node.active_status: 

            playlist_id = data_node.playlistdefault.playlist_id
            print(playlist_id)
            pl_media = PlaylistMedia.query.filter_by(playlist_id=playlist_id).all()
            #media.append(pl_media)
            print(pl_media)
            for m in pl_media:
                if m.media.active_status == 1:
                    media.append({"fileName":m.media.media_name})
            
    except:
        pass
    ################### AD-HOC DATA #########################
    try:
        data_node = Node.query.get_or_404(node)
        if data_node.active_status: 
            #################from ad-hoc schedule###################
            for ad_sc in data_node.adhoc:
                if ad_sc.start_date.date() <= today and today <= ad_sc.end_date.date(): 
                    pl_id = ad_sc.playlist_id
                    ad_media = PlaylistMedia.query.filter_by(playlist_id=pl_id).all()
                    for m in ad_media:
                        print(m.media.media_name)
                        if m.media.active_status == 1:
                            media.append({"fileName":m.media.media_name})
            ########################################################
    except:
        pass


    try:
        media=list({v['fileName']:v for v in media}.values())

    except:
        pass
    return jsonify(media)
###########################################################

#########################GET SCHEDULES#####################
@app.route('/Service2.svc/GetSchedules/<date>/<int:node>')
def nodeGetSchedules(date,node):
    schedule_default = []
    schedule_adhoc_playlist = []
    schedule_adhoc = []
    try: 
        data_node = Node.query.get_or_404(node)
        if data_node.active_status: 

            playlist_id = data_node.playlistdefault.playlist_id
            playlist_active = Playlist.query.get_or_404(playlist_id)
            if playlist_active.active_status:
                #print(playlist_id)
                pl_media = PlaylistMedia.query.filter_by(playlist_id=playlist_id).order_by(PlaylistMedia.order.asc()).all()
                #media.append(pl_media)
                #print(pl_media)
                for m in pl_media:
                    if m.media.active_status == 1:
                        schedule_default.append({"Duration":str(m.duration),"Group":"0","ItemID":str(m.media.id),"Name":m.media.media_name})
    except:
        pass


    ####################AD-HOC SCHEDULE##########################
    try: 
        today = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        data_node = Node.query.get_or_404(node)

        if data_node.active_status: 
            for ad_sc in data_node.adhoc:
                if ad_sc.start_date.date() <= today <= ad_sc.end_date.date(): 
                    pl_id = ad_sc.playlist_id
                    playlist_active = Playlist.query.get_or_404(pl_id)
                    if playlist_active.active_status:
                        ad_media = PlaylistMedia.query.filter_by(playlist_id=pl_id).order_by(PlaylistMedia.order.asc()).all()
                        #media.append(pl_media)
                        #print(pl_media)
                        for m in ad_media:
                            if m.media.active_status == 1:
                                schedule_adhoc.append({"Duration":str(m.duration),"Group":"0","ItemID":str(m.media.id),"Name":m.media.media_name})
    
                        schedule_adhoc_playlist.append({"End":ad_sc.end_time,"PlayItems":schedule_adhoc,"Start":ad_sc.start_time})
    except:
        pass
    list = [{"Default":[],"Panel":0,"Schedule":[]},{"Default":[],"Panel":1,"Schedule":[]},{"Default":[],"Panel":2,"Schedule":[]}]    
    list[2]["Default"] = schedule_default # For pannel 2 FULL ADD
    list[2]["Schedule"] = schedule_adhoc_playlist
    return jsonify(list)

###########################################################


########################GET NEWS###########################
@app.route('/Service2.svc/GetNews/<int:node>')
def nodeGetNews(node):
    news_list = []
    try: 
        data_node = Node.query.get_or_404(node)
        if data_node.active_status: 

            branch = Branch.query.get_or_404(data_node.branch_id)
            news = branch.news
            today = datetime.datetime.now().date()
            for n in news:
                if n.active_status:
                    # print(n.body)
                    # print(n.id)
                    # print(today)
                    # print(n.start_date.date())
                    # print(n.end_date.date())
                    # print(n.never_expire)

                    if n.never_expire:
                        news_list.append({"Body":n.body,"Id":str(n.id)})

                    elif (n.start_date.date() <= today <= n.end_date.date()):
                        news_list.append({"Body":n.body,"Id":str(n.id)})
                    else:
                        pass
    except:
        pass

    return jsonify(news_list)

###########################################################

#######################GET NODE STATUS#####################
@app.route('/Service2.svc/UpdateNodeStatus/<int:node>')
def nodeGetStatus(node):
    data = { }
    try:
        node_active = Node.query.get_or_404(node)
        if node_active.active_status: 
            node_status = NodeStatus.query.filter_by(node_id=node).first()
            adv = node_status.advances
            apr = node_status.application_restart 
            bgd = node_status.background_downloading
            curr = node_status.currency
            dad = node_status.delete_all_data
            dvr = node_status.device_restart
            nws = node_status.news
            pro = node_status.product
            ns_id = node_status.id

            data = {
                "Advances": str(int(adv)),
                "ApplicationRestart": str(int(apr)),
                "BackgroundDownloading": str(int(bgd)),
                "Currency": str(int(curr)),
                "DeleteAllData": str(int(dad)),
                "DeviceRestart": str(int(dvr)),
                "News": str(int(nws)),
                "Product": str(int(pro))
            }

        ### UPDATE TABLE ###
            ns_update = NodeStatus.query.get_or_404(ns_id)
            ns_update.last_online = datetime.datetime.now()
            ns_update.advances = 0
            ns_update.application_restart = 0
            ns_update.background_downloading = 0
            ns_update.currency = 0
            ns_update.delete_all_data = 0
            ns_update.device_restart = 0
            ns_update.news = 0
            ns_update.product = 0


            db.session.commit()
    except:
        pass

    return jsonify(data)

###########################################################


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Custom 403 error handler
@app.errorhandler(403)
def forbidden_error(e):
    # Flash the message
    flash('You are not authorized !', 'danger')
    # Redirect to a safe page (e.g., homepage or login)
    return redirect(url_for('home'))
#######################################################################
#######################################################################
#######################################################################


# utc_time = datetime.utcnow()
# user_timezone = 'America/New_York'
# localized_time = convert_to_user_timezone(utc_time, user_timezone)
# print(localized_time)
