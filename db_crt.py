from signage import app, db, bcrypt  # Adjust based on your actual app and db import
from signage.models import User, Settings, Role, Permission

# Push the application context
with app.app_context():
    try:
        db.create_all()
        print("Database created successfully.")
    except Exception as e:
        print(f"Error creating the database: {e}")

    db_path = db.engine.url.database
    
    print(f"The SQLite database is located at: {db_path}")




    ### Create Permissions
    permissions = [
        Permission(name='manage_users'),
        Permission(name='manage_content'),
        Permission(name='manage_settings'),
        Permission(name='manage_configuration'),
        Permission(name='manage_schedule'),
        Permission(name='manage_news'),
        Permission(name='view_reports'),
        Permission(name='manage_report'),
        Permission(name='manage_system'),
    ]
    
    for permission in permissions:
        db.session.add(permission)
    db.session.commit()
    print("Permissions added.")


    ### Crete Roles
    manage_users_perm = Permission.query.filter_by(name='manage_users').first()
    manage_content_perm = Permission.query.filter_by(name='manage_content').first()
    manage_settings_perm = Permission.query.filter_by(name='manage_settings').first()
    manage_configuration_perm = Permission.query.filter_by(name='manage_configuration').first()
    manage_schedule_perm = Permission.query.filter_by(name='manage_schedule').first()
    manage_news_perm = Permission.query.filter_by(name='manage_news').first()
    view_reports_perm = Permission.query.filter_by(name='view_reports').first()
    manage_report_perm = Permission.query.filter_by(name='manage_report').first()
    manage_system_perm = Permission.query.filter_by(name='manage_system').first()

    # SuperAdmin Role: Full permissions
    Superadmin_role = Role(name='SuperAdmin')
    Superadmin_role.permissions = [
        manage_users_perm, manage_content_perm, manage_settings_perm,
        manage_configuration_perm, manage_schedule_perm, manage_news_perm,
        view_reports_perm, manage_report_perm, manage_system_perm
    ]


    # Admin Role: Full permissions
    admin_role = Role(name='Admin')
    admin_role.permissions = [
        manage_users_perm, manage_content_perm, manage_settings_perm,
        manage_configuration_perm, manage_schedule_perm, manage_news_perm,
        view_reports_perm, manage_report_perm
    ]


    # Editor Role: Manage content, news, schedule, and view reports
    editor_role = Role(name='Editor')
    editor_role.permissions = [
        manage_content_perm, manage_schedule_perm, manage_news_perm,
        view_reports_perm
    ]


    # Viewer Role: Only view reports
    viewer_role = Role(name='Viewer')
    viewer_role.permissions = [view_reports_perm]

    # Add roles to session
    db.session.add(Superadmin_role)
    db.session.add(admin_role)
    db.session.add(editor_role)
    db.session.add(viewer_role)
    db.session.commit()
    print("Roles added.")


    # Retrieve roles
    super_admin_role = Role.query.filter_by(name='SuperAdmin').first()


    if not super_admin_role:
        print("SuperAdmin role does not exist in the database.")
        raise ValueError("SuperAdmin role does not exist")

    # create a super user
    hashed_password = bcrypt.generate_password_hash('superadmin').decode('utf-8')


    settings_update = Settings(version="2.0",company_name="1xtec")
    # company = Company(name="1xtec")

    user_2 = User(firstname='SuperAdmin', email='admin@1xtec.com',
                  username='superadmin', password=hashed_password,active_status=True,role_id=super_admin_role.id) 

    db.session.add(user_2)
    db.session.add(settings_update)
    # db.session.add(company)
    db.session.commit()
    db.session.close()


