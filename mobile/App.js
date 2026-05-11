import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider } from './src/context/AuthContext';

import HomeScreen from './src/screens/HomeScreen';
import NewsDetailScreen from './src/screens/NewsDetailScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import AdminModerationScreen from './src/screens/AdminModerationScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <AuthProvider>
      <NavigationContainer>
        <Stack.Navigator 
          initialRouteName="Home"
          screenOptions={{
            headerStyle: { backgroundColor: '#1B3C53' },
            headerTintColor: '#FFF',
            headerTitleStyle: { fontWeight: 'bold' },
          }}
        >
          <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Canacintra' }} />
          <Stack.Screen name="NewsDetail" component={NewsDetailScreen} options={{ title: 'Noticia' }} />
          <Stack.Screen name="Login" component={LoginScreen} options={{ title: 'Ingresar' }} />
          <Stack.Screen name="Register" component={RegisterScreen} options={{ title: 'Registro' }} />
          <Stack.Screen name="AdminModeration" component={AdminModerationScreen} options={{ title: 'Moderación' }} />
        </Stack.Navigator>
      </NavigationContainer>
    </AuthProvider>
  );
}
