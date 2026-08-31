const express = require('express');
const session = require('express-session');
const passport = require('passport');
const OIDCStrategy = require('passport-azure-ad').OIDCStrategy;
const cors = require('cors');
require('dotenv').config();

const app = express();

// Enable CORS for your Angular/Frontend application
app.use(cors({
    origin: 'http://localhost:4200', // Update to your frontend URL
    credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Express Session Configuration
app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false } // Set to true if using HTTPS in production
}));

app.use(passport.initialize());
app.use(passport.session());

// Passport Session Serialization
passport.serializeUser((user, done) => {
    done(null, user);
});

passport.deserializeUser((obj, done) => {
    done(null, obj);
});

// Configure Microsoft Entra ID OIDC Strategy
passport.use(new OIDCStrategy({
    identityMetadata: `https://login.microsoftonline.com/${process.env.TENANT_ID}/v2.0/.well-known/openid-configuration`,
    clientID: process.env.CLIENT_ID,
    responseType: 'code',
    responseMode: 'query',
    redirectUrl: process.env.REDIRECT_URI,
    allowHttpForRedirectUrl: true, // Set to false in production with HTTPS
    clientSecret: process.env.CLIENT_SECRET,
    scope: ['profile', 'offline_access', 'User.Read'],
    passReqToCallback: false
},
(iss, sub, profile, accessToken, refreshToken, params, done) => {
    // 'profile' contains the claims returned from Microsoft Entra ID
    // You can map fields here to populate your forms later
    const userData = {
        email: profile._json.email || profile._json.preferred_username,
        displayName: profile.displayName,
        firstName: profile.name.givenName,
        lastName: profile.name.familyName,
        jobTitle: profile._json.jobTitle || '',
        department: profile._json.department || '',
        officeLocation: profile._json.officeLocation || ''
    };

    return done(null, userData);
}));

// ==========================================
// ROUTES
// ==========================================

// 1. Trigger Login: Automatically redirects to Microsoft Entra ID
app.get('/auth/microsoft', passport.authenticate('azuread-openidconnect', {
    failureRedirect: '/'
}));

// 2. Microsoft Callback Route: Handles response after successful login
app.get('/auth/microsoft/callback',
    passport.authenticate('azuread-openidconnect', {
        failureRedirect: '/login-failure'
    }),
    (req, res) => {
        // Successful authentication, redirect back to frontend with user data or session set
        res.redirect('http://localhost:4200/dashboard'); // or your form route
    }
);

// 3. API endpoint for Frontend to fetch logged-in user's Entra ID profile details
app.get('/api/current-user', (req, res) => {
    if (req.isAuthenticated()) {
        res.json({ isAuthenticated: true, user: req.user });
    } else {
        res.status(401).json({ isAuthenticated: false, message: 'Not authenticated' });
    }
});

// 4. Logout route
app.get('/auth/logout', (req, res, next) => {
    req.logout((err) => {
        if (err) { return next(err); }
        res.redirect('http://localhost:4200');
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});