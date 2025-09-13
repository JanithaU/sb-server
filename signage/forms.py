from datetime import datetime
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, DateTimeField, IntegerField, FloatField, TimeField,FieldList,FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from signage.models import User, branchGroup, Branch, News, Node, Playlist, Media
from flask_login import login_user, current_user


class UserForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(max=20)])
	firstname = StringField('Name',  
		validators=[DataRequired(), Length(min=2, max=20)])
	password = PasswordField('Password', 
		validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])

	role_id = IntegerField('User Role', 
		validators=[DataRequired()])
class UserRegistrationForm(FlaskForm):
	firstname = StringField('Name',  
		validators=[DataRequired(), Length(min=2, max=20)])
	username = StringField('Username', 
		validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email',
		validators=[DataRequired(), Email()])
	password = PasswordField('Password', 
		validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',
		validators=[DataRequired(), EqualTo('password')])
	active_status = BooleanField('Active')
	role_id = IntegerField('User Role', 
		validators=[DataRequired()])
	submit = SubmitField('Add User')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one. ')

	def validate_email(self, email):
		email = User.query.filter_by(email=email.data).first()
		if email:
			raise ValidationError('That email is taken. Please choose a different one. ')




class UserUpdateForm(FlaskForm):
	firstname = StringField('Name',  
		validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email',
		validators=[DataRequired(), Email()])
	active_status = BooleanField('Active')
	
	# role_id = IntegerField('User Role', 
	# validators=[DataRequired()])
	submit = SubmitField('Update User')

	# def validate_username(self, username):
	# 	user = User.query.filter_by(username=username.data).first()
	# 	print(user.id)
	# 	if user:
	# 		raise ValidationError('Test. ')

	# def validate_email(self, email):
	# 	email = User.query.filter_by(email=email.data).first()
	# 	if email:
	# 		raise ValidationError('That email is taken. Please choose a different one. ')





class LoginForm(FlaskForm):
	username = StringField('Username', 
		validators=[DataRequired(), Length(min=2, max=20)])

	password = PasswordField('Password', 
		validators=[DataRequired()])

	submit = SubmitField('Login')


############ Branch Group ###############


class AddBranchGroupForm(FlaskForm):
	branch_group_name = StringField('Group Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	submit = SubmitField('Add Group')

	def validate_branch_group_name(self, branch_group_name):
		bGG = branchGroup.query.filter_by(branch_group_name=branch_group_name.data).first()
		if bGG:
			raise ValidationError('That Branch Group is taken. Please choose a different one. ')



class UpdateBranchGroupForm(FlaskForm):
	branch_group_name = StringField('Group Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	submit = SubmitField('Update Group')

#	def validate_branch_group_name(self, branch_group_name):
#		bGG = branchGroup.query.filter_by(branch_group_name=branch_group_name.data).first()
#		if bGG:
#			raise ValidationError('That Branch Group is taken. Please choose a different one. ')




############### Branch Group End ###############

############### Branch #################

class AddBranchForm(FlaskForm):
	branch_group_id = IntegerField('Branch Group', 
		validators=[DataRequired()])
	branch_name = StringField('Branch Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	submit = SubmitField('Add Branch')


	def validate_branch_name(self, branch_name):
		print(branch_name)
		bGG = Branch.query.filter_by(branch_name=branch_name.data, branch_group_id=self.branch_group_id.data).first()
		if bGG:
			raise ValidationError('Branch Duplicate in '+str(bGG.group.branch_group_name)+'. Please choose a different one. ')



class UpdateBranchForm(FlaskForm):
	branch_group_id = IntegerField('Branch Group', 
		validators=[DataRequired()])
	branch_name = StringField('Branch Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	submit = SubmitField('Update Branch')



class AddNodeForm(FlaskForm):
	branch_group_id = StringField('Branch Group', 
		validators=[DataRequired(), Length(min=1, max=20)])
	branch_id = StringField('Branch ', 
		validators=[DataRequired(), Length(min=1, max=20)])
	node_name = StringField('Node Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	node_password = PasswordField('Node Password', 
		validators=[DataRequired()])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Add Node') 


	def validate_node_name(self, node_name):
		bGG = Node.query.filter_by(node_name=node_name.data).first()
		if bGG:
			raise ValidationError('That Node is taken. Please choose a different one. ')




class UpdateNodeForm(FlaskForm):
	branch_group_id = StringField('Branch Group', 
		validators=[DataRequired(), Length(min=1, max=20)])
	branch_id = StringField('Branch ', 
		validators=[DataRequired(), Length(min=1, max=20)])
	node_name = StringField('Node Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	node_password = PasswordField('Node Password', 
		validators=[DataRequired()])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Update Node') 


class AddMediaForm(FlaskForm):
	media_name = StringField('Media Name', 
		validators=[DataRequired(), Length(min=2, max=60)])
	media_thumb_name = StringField('Thumb Name ')
	media_type = StringField('Type', 
		validators=[Length(min=0, max=20)])
	media_file_size = IntegerField('File Size', 
		validators=[Length(min=0, max=10)])
	media_duration = StringField('Time',default='00:00:00')
	media_file=FileField('Media File',validators=[FileAllowed(['jpg','jpeg','mp4']), FileRequired()])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Add Media') 

	def validate_media_name(self, media_name):
		media = Media.query.filter_by(media_name=media_name.data).first()
		if media:
			raise ValidationError('That media name is taken. Please choose a different one. ')

	
class UpdateMediaForm(FlaskForm):
	media_name = StringField('Media Name', 
		validators=[DataRequired(), Length(min=2, max=60)])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Update Media') 


class AddPlaylistForm(FlaskForm):
	playlist_name = StringField('Playlist Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	playlist_type = StringField('Type', 
		validators=[Length(min=0, max=20)], default='FullAd')
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Add Playlist') 


	def validate_playlist_name(self, playlist_name):
		bGG = Playlist.query.filter_by(playlist_name=playlist_name.data).first()
		if bGG:
			raise ValidationError('That Playlist is taken. Please choose a different one. ')



class UpdatePlaylistForm(FlaskForm):
	playlist_name = StringField('Playlist Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	playlist_type = StringField('Type', 
		validators=[Length(min=0, max=20)], default='FullAd')
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Update Playlist') 



class AddTemplateForm(FlaskForm):
	template_name = StringField('Playlist Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	description = TextAreaField('Description', validators=[Length(max=200)])
	active_status = BooleanField('Active')
	added_date = DateTimeField('Date', format='%Y-%m-%d', default=datetime.utcnow)
	submit = SubmitField('Add Template') 


class AddTemplateItemForm(FlaskForm):
	template_items = StringField('Playlist Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	template_duration = DateTimeField('Duration', format = "%d%b%Y %H:%M",default= datetime.utcnow)
	submit = SubmitField('Add Template') 



class AddNewsForm(FlaskForm):
	heading = StringField('Topic', 
		validators=[DataRequired(), Length(min=2, max=20)])
	body = TextAreaField('Body', validators=[Length(max=255), DataRequired()])
	start_date = DateTimeField('Start Date',validators=[DataRequired()], format='%Y-%m-%d')
	end_date = DateTimeField('End Date', format='%Y-%m-%d')
	never_expire = BooleanField('Never Expire')
	active_status = BooleanField('Active')
	order = IntegerField('News Order')
	submit = SubmitField('Add News') 




class UpdateNewsForm(FlaskForm):
	heading = StringField('Topic', 
		validators=[DataRequired(), Length(min=2, max=20)])
	body = TextAreaField('Body', validators=[Length(max=255), DataRequired()])
	start_date = DateTimeField('Start Date',validators=[DataRequired()], format='%Y-%m-%d')
	end_date = DateTimeField('End Date', format='%Y-%m-%d')
	never_expire = BooleanField('Never Expire')
	active_status = BooleanField('Active')
	order = IntegerField('News Order')
	submit = SubmitField('Update News') 




class UpdateSettings(FlaskForm):
	time_zone = StringField('Time Zone', 
		validators=[DataRequired()])
	download_stop = StringField('Download Stop Time', 
		validators=[DataRequired()])
	download_start = StringField('Download Start Time', 
		validators=[DataRequired()])
	image_duration = IntegerField('Default Image Duration')
	file_size_limit = FloatField('File Size Limit(MB)')
	file_size_limit_total = FloatField('Total File Size Limit(MB)')
	submit = SubmitField('Update Settings')



class AddAddhocForm(FlaskForm):
	addhoc_name = StringField('Schedule Name', 
		validators=[DataRequired(), Length(min=2, max=20)])
	playlist_id = StringField('Playlist ', 
		validators=[DataRequired(), Length(min=1, max=20)])
	start_date = DateTimeField('Start Date',validators=[DataRequired()], format='%Y-%m-%d')
	end_date = DateTimeField('End Date',validators=[DataRequired()], format='%Y-%m-%d')
	start_time = StringField('Start Time', 
		validators=[DataRequired()])
	end_time = StringField('End Time', 
		validators=[DataRequired()])
	description = TextAreaField('Description', validators=[Length(max=200)])
	submit = SubmitField('Add AdHoc') 
